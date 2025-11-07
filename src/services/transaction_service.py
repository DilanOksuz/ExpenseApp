from datetime import datetime
from typing import List, Dict
from src.core.config import TRANSACTIONS_FILE
from src.storage.txt_store import read_rows, append_row
from src.core.ids import new_id
from src.core.validation import (
    TRANSACTION_DATE_FMT,
    validate_type_basic,
    validate_amount_basic,
    validate_date_basic,
    validate_description_basic,
    validate_category_id_basic,
)
from src.services import category_service

def list_categories_for_type(user_id: str, type_: str) -> List[Dict]:
    type_ = (type_ or "").strip().lower()
    out: List[Dict] = []
    for c in category_service.list_categories(user_id):
        if c.get("type") == type_:
            out.append({"id": c["category_id"], "name": c["name"]})
    return out

def get_category_name_by_id(user_id: str, category_id):
    if not category_id:
        return None
    for c in category_service.list_categories(user_id):
        if c["category_id"] == category_id:
            return c["name"]
    return None

def _ensure_category_belongs_to_user(user_id: str, category_id, type_: str) -> None:
    if not category_id:
        return
    type_ = (type_ or "").strip().lower()
    for c in category_service.list_categories(user_id):
        if c["category_id"] == category_id and c["type"] == type_:
            return
    raise ValueError("Kategori bu kullanıcıya ait değil veya tür uyuşmuyor.")

def create_transaction(
    user_id: str,
    type_: str,
    amount_str: str,
    date_str,
    category_id,
    description: str = "",
):
    type_ = validate_type_basic(type_)
    amount = validate_amount_basic(amount_str)
    date_out = validate_date_basic(date_str)
    category_id = validate_category_id_basic(category_id)
    description = validate_description_basic(description)

    _ensure_category_belongs_to_user(user_id, category_id, type_)

    tid = new_id()
    row = [
        tid,
        (user_id or "").strip(),
        date_out,
        type_,
        f"{amount:.2f}",
        (category_id or ""),
        description,
    ]
    append_row(TRANSACTIONS_FILE, row)

    return {
        "transaction_id": tid,
        "user_id": user_id,
        "date": date_out,
        "type": type_,
        "amount": amount,
        "category_id": category_id,
        "description": description,
    }

def create_income(user_id: str, amount_str: str, date_str, category_id, description=""):
    return create_transaction(user_id, "income", amount_str, date_str, category_id, description)

def create_expense(user_id: str, amount_str: str, date_str, category_id, description=""):
    return create_transaction(user_id, "expense", amount_str, date_str, category_id, description)

def _parse_date_for_sort(date_s: str) -> datetime:
    try:
        return datetime.strptime((date_s or "").strip(), TRANSACTION_DATE_FMT)
    except Exception:
        return datetime.min

def _parse_amount_no_try(amount_s: str) -> float:
    s = (amount_s or "").replace(",", ".").strip()
    if not s:
        return 0.0
    parts = s.split(".")
    if any(not p.isdigit() for p in parts if p != "") or len(parts) > 2:
        return 0.0
    try:
        return float(s)
    except Exception:
        return 0.0

def list_transactions(user_id: str, type_=None) -> List[Dict]:
    items: List[Dict] = []
    for row in read_rows(TRANSACTIONS_FILE):
        if not row or row[0].lstrip().startswith("#"):
            continue
        if len(row) < 6:
            continue
        tid, uid, date_s, t, amount_s, cat_id = row[:6]
        desc = row[6] if len(row) >= 7 else ""
        if (uid or "").strip() != (user_id or "").strip():
            continue
        if type_ and (t or "").strip() != (type_ or "").strip():
            continue
        amt = _parse_amount_no_try(amount_s)
        category_id = (cat_id or "").strip() or None
        items.append({
            "transaction_id": (tid or "").strip(),
            "user_id": (uid or "").strip(),
            "date": (date_s or "").strip(),
            "type": (t or "").strip(),
            "amount": amt,
            "category_id": category_id,
            "description": (desc or "").strip(),
        })
    items.sort(key=lambda x: _parse_date_for_sort(x["date"]))
    return items

def list_incomes(user_id: str) -> List[Dict]:
    return list_transactions(user_id, "income")

def list_expenses(user_id: str) -> List[Dict]:
    return list_transactions(user_id, "expense")

def delete_transaction_by_id(txn_id: str, user_id: str) -> None:
    rows = read_rows(TRANSACTIONS_FILE)
    new_rows = []
    deleted = False
    for row in rows:
        if not row or row[0].lstrip().startswith("#"):
            new_rows.append(row)
            continue
        if len(row) >= 2 and (row[0] or "").strip() == (txn_id or "").strip() and (row[1] or "").strip() == (user_id or "").strip():
            deleted = True
            continue
        new_rows.append(row)
    if not deleted:
        raise ValueError("Kayıt bulunamadı.")
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        for r in new_rows:
            f.write("\t".join(r) + "\n")

def _materialize_user_type_rows_with_pointers(user_id: str, type_: str):
    rows = read_rows(TRANSACTIONS_FILE)
    pointers = []
    for i, row in enumerate(rows):
        if not row or row[0].lstrip().startswith("#"):
            continue
        if len(row) < 6:
            continue
        tid, uid, date_s, t, amount_s, cat_id = row[:6]
        desc = row[6] if len(row) >= 7 else ""
        if (uid or "").strip() != (user_id or "").strip():
            continue
        if (t or "").strip() != (type_ or "").strip():
            continue
        amt = _parse_amount_no_try(amount_s)
        parsed = {
            "transaction_id": (tid or "").strip(),
            "user_id": (uid or "").strip(),
            "date": (date_s or "").strip(),
            "type": (t or "").strip(),
            "amount": amt,
            "category_id": ((cat_id or "").strip() or None),
            "description": (desc or "").strip(),
        }
        pointers.append((i, parsed))
    return rows, pointers

def enumerate_transactions_for_edit(user_id: str, type_: str) -> List[Dict]:
    _, pointers = _materialize_user_type_rows_with_pointers(user_id, type_)
    out: List[Dict] = []
    for idx, (_, item) in enumerate(pointers, start=1):
        out.append({
            "index": idx,
            "transaction_id": item["transaction_id"],
            "date": item["date"],
            "amount": item["amount"],
            "category_id": item["category_id"],
            "category_name": get_category_name_by_id(user_id, item["category_id"]) or "(yok)",
            "description": item["description"],
        })
    return out

def update_transaction_by_index(user_id: str, type_: str, index: int, field: str, new_value) -> None:
    if field not in {"date", "amount", "category_id", "description"}:
        raise ValueError("Geçersiz alan adı.")
    rows, pointers = _materialize_user_type_rows_with_pointers(user_id, type_)
    if index < 1 or index > len(pointers):
        raise ValueError("Geçersiz index.")
    row_pointer, _current = pointers[index - 1]
    row = rows[row_pointer]
    if field == "date":
        row[2] = validate_date_basic(new_value)
    elif field == "amount":
        row[4] = f"{validate_amount_basic(new_value or ''):.2f}"
    elif field == "category_id":
        cid = validate_category_id_basic(new_value)
        _ensure_category_belongs_to_user(user_id, cid, type_)
        row[5] = cid or ""
    elif field == "description":
        row[6] = validate_description_basic(new_value or "")
    with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
