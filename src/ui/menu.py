from getpass import getpass 
from src.services import auth_service


def register_flow():
    print("KAYIT OLUŞTUR")
    user_name = input("Kullanıxı Adı:").strip()
    pw1 = getpass("şifre . ")
    pw2 = getpass("Şifre Tekrarı")

    try:
        user = auth_service.register(user_name, pw1, pw2)
        print("Kayıt başarılı. ")
    except ValueError as e:
        print(f"Hata:{e}/n")
    except Exception as e:
        print(f"Bilinmeyen Hata {e}/n") 