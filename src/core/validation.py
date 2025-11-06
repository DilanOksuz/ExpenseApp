import re 

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


