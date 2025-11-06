from src.services import auth_service
from src.services import category_service

def ask(prompt: str) -> str:
    return input(prompt).strip()

def register_flow():
    print("KAYIT OLUŞTUR")
    user_name = input("Kullanıcı Adı: ")
    pw1 = input("Şifre: ")
    pw2 = input("Şifre (tekrar): ")

    try:
        user = auth_service.register(user_name, pw1, pw2)
        print("Kayıt başarılı. ")
    except ValueError as e:
        print(f"Hata:{e}\n")
        return None
    except Exception as e:
        print(f"Bilinmeyen Hata {e}\n") 
        return None
    

def login_flow() -> dict | None:
    print("GİRİŞ YAP")
    username = ask("Kullanıcı adı:")
    pw=ask("Şifre")
    try: 
        user = auth_service.login(username, pw)
        print(f"\n Giriş başarılı. Hoş geldin, {user['username']}!\n")
        return user
    except ValueError as e:
        print(f"\n Hata {e}\n")
        return None
    
def welcome_loop() -> dict | None:
    while True:
        print("""GELİR GİDER UYGULAMASI 
              1) Giriş Yap 
              2)Kayıt Ol 
              3) Çıkış
              """)
        choice = ask("Seçiminiz:")
        if choice == "1":
            user = login_flow()
            if user:
                return user
        elif choice =="2":
            register_flow()
        elif choice == "3":
            return None
        else:
            print("Geçersiz Seçim. Lütfen 1,2 veya 3 seçin.")
        

def category_menu(user:dict ) -> None:
    while True:
        print(""" KATEGORİ İŞLEMLERİ
              1)Kategori Ekle
              2)Kategori Listele
              3)Kategori Dpzenle
              4)Kategori Sil
              5)Geri
    """)
        sel = input("Seçiminiz: ").strip()


        if sel == "1":
            name = ask("Kategori adı: ")
            type_ = ask("Kategori (income/expense) : ").lower()
            try:
                cat = category_service.create_category(user["user_id"], name, type_)
                print(f"Eklendi: {cat['name']} [{cat['type']}] (ID: {cat['category_id']})")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata {e}")

        elif sel =="2":
            cats = category_service.list_categories(user["user_id"])
            if not cats:
                print("Hiç kategori yok.")
            else: 
                print("\nID\t\t\t\t\tTÜR\tAD")
                for c in cats:
                    print(f"{c['category_id']}\t{c['type']}\t{c['name']}")

        elif sel == "3":
            old_name = ask("Düzenlenecek kategori adı:")
            type_ = ask("Tür (income/expense) :").lower()
            new_name = ask("Yeni isim:")
            try:
                category_service.update_category_by_name(old_name, new_name, user["user_id"], type_)
                print("Kategori Güncellendi.")
            except ValueError as e:
                print(f"Bilinmeyen Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel =="4":
            name = ask("Silinecek kategori adı")
            type_ = ask("Tür (income/expense):").lower()
            try:
                category_service.delete_category_by_name(name, user["user_id"], type_)
                print("Kategori silindi. ")
            except ValueError as e:
                print(f"Bilinmeyen Hata {e}")
            except Exception as e:
                print(f"Nilinmeyen Hata {e}")


        elif sel == "5":
            break
        else:
            print("yanlış seçim" )
            

def app_menu(user:dict ) -> None:
    while True:
        print(""" ANA MENU
              1)Gelir İşlemleri 
              2)Gider İşlemleri
              3)Kategori Yönetimi
              4)Raporlar
              5)Hesap/oturum
              6)Çıkış

            """)
        secim = ask("Seçiminiz:")

        if secim == "1":
            print("gelir menusu")
        if secim == "2":
            print("gider menusu")
        if secim =="3" : 
            category_menu(user)
        if secim == "4":
            print("rapor menusu oluşturulacak ")
        if secim == "5":
            print("hesap işlemleri olusturulacak. ")
        if secim=="6":
            break