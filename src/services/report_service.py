from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from src.core.validation import TRANSACTION_DATE_FMT
from src.services import transaction_service


def _parse_date(s: str) -> datetime:
    try:
        return datetime.strptime((s or "").strip(), TRANSACTION_DATE_FMT)
    except Exception:
        return datetime.min


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


def by_category(user_id: str, type_: str) -> List[Tuple[str, float]]:
    rows = _filter_by_type(user_id, type_)
    bucket = defaultdict(float)
    for r in rows:
        name = transaction_service.get_category_name_by_id(user_id, r.get("category_id")) or "(yok)"
        bucket[name] += r.get("amount", 0.0)
    out = sorted(bucket.items(), key=lambda x: x[1], reverse=True)
    return [(k, round(v, 2)) for k, v in out]
