from src.core.config import CATEGORIES_FILE, TRANSACTIONS_FILE
from src.core.ids import new_id
from src.core.validation import validate_category_name, normalize_username
from src.storage.txt_store import read_rows, append_row

def _name_exists_for_user(user_id: str, name: str, type_: str) -> bool:
    target = normalize_username(name)
    for row in read_rows(CATEGORIES_FILE):
        if len(row) < 4:
            continue
        _, uid, t, nm = row
        if uid == user_id and t == type_ and normalize_username(nm) == target:
            return True
    return False

def create_category(user_id: str, name: str, type_: str) -> dict:
    validate_category_name(name)
    type_ = type_.lower().strip()
    if type_ not in ("income", "expense"):
        raise ValueError("Kategori türü 'income' veya 'expense' olmalıdır.")
    if _name_exists_for_user(user_id, name, type_):
        raise ValueError("Bu kategori adı zaten kullanılmakta (aynı türde).")

    cid = new_id()
    append_row(CATEGORIES_FILE, [cid, user_id, type_, name.strip()])
    return {"category_id": cid, "user_id": user_id, "type": type_, "name": name.strip()}

def list_categories(user_id: str) -> list[dict]:
    items: list[dict] = []
    for row in read_rows(CATEGORIES_FILE):
        if len(row) < 4:
            continue
        cid, uid, type_, nm = row
        if uid == user_id:
            items.append({"category_id": cid, "user_id": uid, "type": type_, "name": nm})
    return items

def list_category_names_by_type(user_id: str, type_: str) -> list[str]:
    type_ = (type_ or "").strip().lower()
    return [c["name"] for c in list_categories(user_id) if c.get("type") == type_]

def list_category_names_grouped(user_id: str) -> dict:
    inc = [c["name"] for c in list_categories(user_id) if c.get("type") == "income"]
    exp = [c["name"] for c in list_categories(user_id) if c.get("type") == "expense"]
    return {"income": inc, "expense": exp}

def get_category_id_by_name(user_id: str, type_: str, name: str) -> str | None:
    type_ = (type_ or "").strip().lower()
    target = normalize_username(name)
    for c in list_categories(user_id):
        if c.get("type") == type_ and normalize_username(c.get("name", "")) == target:
            return c["category_id"]
    return None

def update_category_by_name(old_name: str, new_name: str, user_id: str, type_: str) -> None:
    validate_category_name(new_name)
    type_ = (type_ or "").lower().strip()
    if type_ not in ("income", "expense"):
        raise ValueError("Tür 'income' veya 'expense' olmalı.")

    rows = read_rows(CATEGORIES_FILE)
    updated = False

    for row in rows:
        if len(row) >= 4:
            cid, uid, t, nm = row
            if uid == user_id and t == type_ and normalize_username(nm) == normalize_username(old_name):
                if _name_exists_for_user(user_id, new_name, t):
                    raise ValueError("Bu isim zaten mevcut .")
                row[3] = new_name.strip()
                updated = True
                break

    if not updated:
        raise ValueError("Kategori bulunamadı.")

    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")

def delete_category_by_name(name: str, user_id: str, type_: str) -> None:
    type_ = (type_ or "").lower().strip()
    if type_ not in ("income", "expense"):
        raise ValueError("Tür 'income' veya 'expense' olmalı.")

    cat_id = get_category_id_by_name(user_id, type_, name)
    if not cat_id:
        raise ValueError("Kategori bulunamadı veya size ait değil.")

    for row in read_rows(TRANSACTIONS_FILE):
        if len(row) >= 6 and (row[5] or "").strip() == cat_id:
            raise ValueError("Bu kategori kayıtlarca kullanılıyor, silinemez.")

    rows = read_rows(CATEGORIES_FILE)
    new_rows = []
    deleted = False

    for row in rows:
        if len(row) >= 4:
            cid, uid, t, nm = row
            if uid == user_id and t == type_ and cid == cat_id:
                deleted = True
                continue
        new_rows.append(row)

    if not deleted:
        raise ValueError("Kategori bulunamadı veya size ait değil.")

    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        for r in new_rows:
            f.write("\t".join(r) + "\n")
