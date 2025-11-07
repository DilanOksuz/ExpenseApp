import re 
from datetime import datetime

def normalize_username(name : str) -> str:
    return (name or "").strip().lower()

def validate_username(name: str):
    name = name or ""
    if not name.strip():
        raise ValueError("Kullanıcı adı boş olamaz.")
    if len(name.strip()) < 5:
        raise ValueError("Kullanıcı adı en az 5 karakter olmalı.")
    if "\t" in name or "\n" in name or "\r" in name:
        raise ValueError("Kullanıcı adında geçersiz karakter var (TAB veya satır sonu).")

def validate_password(pw: str):
    if not pw:
        raise ValueError("Şifre boş olamaz.")
    if len(pw) < 5:
        raise ValueError("Şifre 5 karaktrden az olamaz")
    
def validate_category_name(name:str) -> None:
    if not (name or "").strip():
        raise ValueError("Kategpri adı boş olamaz. ")
    if "\t" in name or "\n" in name or "\r" in name:
        raise ValueError("Kategori adında geçersiz karakter var")

TRANSACTION_DATE_FMT = "%d-%m-%Y" 

def validate_type_basic(type_:str) -> str:
    type_ = (type_ or "").strip().lower()
    if type_ not in ("income","expense" ):
        raise ValueError("Tür 'income' ya da 'expense' olsun" )
    return type_

def validate_amount_basic(amount_str: str) -> float:
    s= (amount_str or "").replace(",",".").strip()
    try:
        val = float(s)
    except Exception:
        raise ValueError("Tutar Geçersiz.")
    if val <= 0:
        raise ValueError("Tutar 0dan büyük olmalı")
    return float(f"{val:.2f}")


def validate_date_basic(date_str: str | None ) -> str:
    s=(date_str or "").strip()
    if not s:
        return datetime.now().strftime(TRANSACTION_DATE_FMT)
    try : 
        dt = datetime.strftime(s, TRANSACTION_DATE_FMT)
    except ValueError:
        raise ValueError(f"Tarih formatı {TRANSACTION_DATE_FMT} olmalı")
    return dt.strftime(TRANSACTION_DATE_FMT)

def validate_description_basic(desc: str | None) -> str:
    desc = (desc or "").strip()
    for ch in ("\t","\r","\n"):
        desc = desc.replace(ch, " ")
    
    if len(desc) > 100:
        raise ValueError("Acıklama 100 karakteri geçmemeli.")
    return desc


def validate_category_id_basic(category_id:str) -> str:
    if category_id is None:
        return None
    cid = (category_id or "").strip()
    if not cid:
        return None 
    if any(c in cid for c in ("\t", "\r", "\n")):
        raise ValueError("Kategori ID geçersiz karakter olamaz")
    return cid
    
