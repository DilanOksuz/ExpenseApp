from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timedelta
from calendar import monthrange
from typing import Dict, List, Tuple, Iterable, Optional

from src.core.validation import TRANSACTION_DATE_FMT
from src.services import transaction_service


def _parse_date(s: str) -> datetime:
    try:
        return datetime.strptime((s or "").strip(), TRANSACTION_DATE_FMT)
    except Exception:
        return datetime.min


def _iter_rows(
    user_id: str,
    type_: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Iterable[Dict]:
    rows = transaction_service.list_transactions(user_id, type_)
    for r in rows:
        dt = _parse_date(r.get("date", ""))
        if start and dt < start:
            continue
        if end and dt > end:
            continue
        yield r


def _sum_by_type(rows: Iterable[Dict]) -> Dict[str, float]:
    inc = exp = 0.0
    for r in rows:
        if r.get("type") == "income":
            inc += r.get("amount", 0.0)
        elif r.get("type") == "expense":
            exp += r.get("amount", 0.0)
    return {
        "income": round(inc, 2),
        "expense": round(exp, 2),
        "net": round(inc - exp, 2),
    }


def totals_all(user_id: str) -> Dict[str, float]:
    return _sum_by_type(_iter_rows(user_id, None, None, None))


def weekly_summary(user_id: str) -> Dict[str, float]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=6)
    end = today + timedelta(hours=23, minutes=59, seconds=59)
    return _sum_by_type(_iter_rows(user_id, None, start, end))


def current_month_summary(user_id: str) -> Dict[str, float]:
    now = datetime.now()
    first = datetime(year=now.year, month=now.month, day=1)
    last_day = monthrange(now.year, now.month)[1]
    last = datetime(year=now.year, month=now.month, day=last_day, hour=23, minute=59, second=59)
    return _sum_by_type(_iter_rows(user_id, None, first, last))


def range_summary(user_id: str, start_str: str, end_str: str) -> Dict[str, float]:
    start = _parse_date(start_str)
    end = _parse_date(end_str)
    if start == datetime.min or end == datetime.min:
        raise ValueError(f"Tarih formatı {TRANSACTION_DATE_FMT} olmalı.")
    if start > end:
        raise ValueError("Başlangıç tarihi, bitişten büyük olamaz.")
    end = end.replace(hour=23, minute=59, second=59)
    return _sum_by_type(_iter_rows(user_id, None, start, end))


def last_12_months_table(user_id: str) -> list[dict]:
    out: list[dict] = []
    today = datetime.now()
    for i in range(11, -1, -1):
        target = today.replace(day=15) - timedelta(days=i * 30)
        yr = target.year
        mo = target.month
        first = datetime(year=yr, month=mo, day=1)
        last_day = monthrange(yr, mo)[1]
        last = datetime(year=yr, month=mo, day=last_day, hour=23, minute=59, second=59)
        sums = _sum_by_type(_iter_rows(user_id, None, first, last))
        out.append({
            "period": f"{yr}-{mo:02d}",
            "income": sums["income"],
            "expense": sums["expense"],
            "balance": sums["net"],
        })
    return out


def by_category(
    user_id: str,
    type_: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[Tuple[str, float]]:
    t_filter = (type_ or "").strip().lower()
    start_dt = _parse_date(start) if start else None
    end_dt = _parse_date(end) if end else None
    if end_dt:
        end_dt = end_dt.replace(hour=23, minute=59, second=59)
    rows = _iter_rows(user_id, t_filter, start_dt, end_dt)
    bucket = defaultdict(float)
    for r in rows:
        name = transaction_service.get_category_name_by_id(user_id, r.get("category_id")) or "(yok)"
        bucket[name] += float(r.get("amount", 0.0))
    out = sorted(bucket.items(), key=lambda x: x[1], reverse=True)
    return [(k, round(v, 2)) for k, v in out]


def _filter_by_type(user_id: str, type_: str) -> List[Dict]:
    return transaction_service.list_transactions(user_id, type_)


def total_by_type(user_id: str, type_: str) -> float:
    rows = _filter_by_type(user_id, type_)
    return round(sum(r.get("amount", 0.0) for r in rows), 2)


def total_income(user_id: str) -> float:
    return total_by_type(user_id, "income")


def total_expense(user_id: str) -> float:
    return total_by_type(user_id, "expense")


def balance(user_id: str) -> float:
    return round(total_income(user_id) - total_expense(user_id), 2)


def totals_last_n_days(user_id: str, n: int) -> Dict[str, float]:
    rows = transaction_service.list_transactions(user_id, None)
    cutoff = datetime.now() - timedelta(days=n)
    inc = exp = 0.0
    for r in rows:
        dt = _parse_date(r.get("date", ""))
        if dt >= cutoff:
            if r.get("type") == "income":
                inc += r.get("amount", 0.0)
            elif r.get("type") == "expense":
                exp += r.get("amount", 0.0)
    return {
        "income": round(inc, 2),
        "expense": round(exp, 2),
        "net": round(inc - exp, 2),
    }


def monthly_breakdown(user_id: str, year: int, type_: str | None = None) -> Dict[int, float]:
    rows = transaction_service.list_transactions(user_id, type_)
    totals = {m: 0.0 for m in range(1, 13)}
    for r in rows:
        dt = _parse_date(r.get("date", ""))
        if dt.year == year:
            totals[dt.month] += r.get("amount", 0.0)
    return {m: round(v, 2) for m, v in totals.items()}
