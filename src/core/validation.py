import re 

def normalize_username(name : str) -> str:
    return (name or "").strip().lower()

def validate_username(name: str):
    if not name.strip():
        raise ValueError("Kullanıcı adı boş olamaz")
    if len(name.strip)<5:
        raise ValueError("Kullancı adı 5 karakterden fazla olmalı ")

def validate_password(pw: str):
    if not pw:
        raise ValueError("Şifre boş olamaz.")
    if len(pw) < 5:
        raise ValueError("Şifre 5 karaktrden az olamaz")
    


