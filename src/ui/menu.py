from src.services import auth_service
from src.services import category_service
from src.services import transaction_service
from src.services import report_service


def ask(prompt: str) -> str:
    return input(prompt).strip()


def register_flow():
    print("KAYIT OLUŞTUR")
    user_name = input("Kullanıcı Adı: ")
    pw1 = input("Şifre: ")
    pw2 = input("Şifre (tekrar): ")
    try:
        auth_service.register(user_name, pw1, pw2)
        print("Kayıt başarılı.")
    except ValueError as e:
        print(f"Hata: {e}\n")
        return None
    except Exception as e:
        print(f"Bilinmeyen Hata: {e}\n")
        return None


def login_flow() -> dict | None:
    print("GİRİŞ YAP")
    username = ask("Kullanıcı adı: ")
    pw = ask("Şifre: ")
    try:
        user = auth_service.login(username, pw)
        print(f"\nGiriş başarılı. Hoş geldin, {user['username']}!\n")
        return user
    except ValueError as e:
        print(f"\nHata: {e}\n")
        return None


def welcome_loop() -> dict | None:
    while True:
        print("""GELİR GİDER UYGULAMASI
  1) Giriş Yap
  2) Kayıt Ol
  3) Çıkış
""")
        choice = ask("Seçiminiz: ")
        if choice == "1":
            user = login_flow()
            if user:
                return user
        elif choice == "2":
            register_flow()
        elif choice == "3":
            return None
        else:
            print("Geçersiz seçim.")


def category_menu(user: dict) -> None:
    def pick_index_from_names(title: str, names: list[str]) -> str | None:
        print(f"\n{title}")
        if not names:
            print("(liste boş)")
            return None
        for i, nm in enumerate(names, 1):
            print(f"{i}) {nm}")
        while True:
            s = ask("Seçim (numara): ")
            try:
                idx = int(s)
                if 1 <= idx <= len(names):
                    return names[idx - 1]
            except ValueError:
                pass
            print("Geçersiz seçim.")

    def ask_type_menu() -> str:
        while True:
            print("Tür seçin:\n  1) Gelir (income)\n  2) Gider (expense)\n")
            t = ask("Seçiminiz: ").strip()
            if t == "1":
                return "income"
            if t == "2":
                return "expense"
            print("Geçersiz seçim.")

    while True:
        print("""KATEGORİ İŞLEMLERİ
  1) Kategori Ekle
  2) Kategori Listele (türe göre)
  3) Kategori Düzenle (tür → indeks)
  4) Kategori Sil (tür → indeks → onay)
  5) Geri
""")
        sel = ask("Seçiminiz: ").strip()

        if sel == "1":
            name = ask("Kategori adı: ").strip()
            type_ = ask_type_menu()
            try:
                cat = category_service.create_category(user["user_id"], name, type_)
                print(f"Eklendi: {cat['name']} [{cat['type']}] (ID: {cat['category_id']})")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel == "2":
            type_ = ask_type_menu()
            names = category_service.list_category_names_by_type(user["user_id"], type_)
            if not names:
                print(f"{type_} türünde kategori yok.")
            else:
                print(f"\n{type_.upper()} kategorileri:")
                for nm in names:
                    print(f" - {nm}")

        elif sel == "3":
            type_ = ask_type_menu()
            names = category_service.list_category_names_by_type(user["user_id"], type_)
            if not names:
                print(f"{type_} türünde kategori yok.")
                continue
            old_name = pick_index_from_names(f"{type_.upper()} kategorileri (düzenleme):", names)
            if not old_name:
                continue
            new_name = ask("Yeni isim: ").strip()
            try:
                category_service.update_category_by_name(old_name, new_name, user["user_id"], type_)
                print("Kategori güncellendi.")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel == "4":
            type_ = ask_type_menu()
            names = category_service.list_category_names_by_type(user["user_id"], type_)
            if not names:
                print(f"{type_} türünde kategori yok.")
                continue
            name = pick_index_from_names(f"{type_.upper()} kategorileri (silme):", names)
            if not name:
                continue
            ok = ask(f"'{name}' kategorisini silmek istediğinize emin misiniz? (yes/no): ").lower()
            if ok not in ("y", "yes", "e", "evet"):
                print("İşlem iptal edildi.")
                continue
            try:
                category_service.delete_category_by_name(name, user["user_id"], type_)
                print("Kategori silindi.")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel == "5":
            break
        else:
            print("Yanlış seçim.")


def transaction_menu(user: dict, type_: str) -> None:
    type_ = (type_ or "").strip().lower()
    header = "GELİR" if type_ == "income" else "GİDER"

    def pick_from_list(title, items, allow_none=False):
        print(f"\n{title}")
        if allow_none:
            print("0) (Boş bırak)")
        if not items:
            
            print("(liste boş)")
            return None if allow_none else None
        for i, (_, label) in enumerate(items, 1):
            print(f"{i}) {label}")
        while True:
            s = ask("Seçim (numara): ")
            try:
                idx = int(s)
                if allow_none and idx == 0:
                    return None
                if 1 <= idx <= len(items):
                    return items[idx - 1][0]
            except ValueError:
                pass
            print("Geçersiz seçim.")

    def print_txn_table(rows):
        if not rows:
            print("\n(liste boş)")
            return
        col_cat = max(8, max(len(r["category_name"] or "") for r in rows))
        col_desc = 30
        print()
        print(f"{'#':>3} {'TARİH':<12} {'TUTAR':>12}  {'KATEGORİ':<{col_cat}} {'AÇIKLAMA':<{col_desc}}")
        print("-" * (3 + 1 + 12 + 1 + 12 + 2 + col_cat + 1 + col_desc))
        for r in rows:
            date = r["date"]
            amt = f"{float(r['amount']):.2f}"
            cat = (r["category_name"] or "(yok)")
            desc = (r["description"] or "")
            if len(desc) > col_desc:
                desc = desc[: col_desc - 1] + "…"
            print(f"{r['index']:>3} {date:<12} {amt:>12}  {cat:<{col_cat}} {desc:<{col_desc}}")

    def choose_edit_field():
        print("""
Hangi alanı düzenlemek istersiniz?
  1) Açıklama
  2) Kategori
  3) Tutar
  4) Tamamla
  5) Vazgeç
""")
        s = ask("Seçiminiz: ").strip()
        if s == "1":
            return "description"
        if s == "2":
            return "category_id"
        if s == "3":
            return "amount"
        if s == "4":
            return "commit"
        if s == "5":
            return "cancel"
        print("Geçersiz seçim.")
        return None

    while True:
        print(f"""{header} İŞLEMLERİ
  1) {header} Ekle
  2) {header} Sil
  3) {header} Düzenle
  4) {header} Listele
  5) Geri
""")
        sel = ask("Seçiminiz: ").strip()

        if sel == "1":
            cats = category_service.list_categories(user["user_id"])
            cats_of_type = [(c["category_id"], c["name"]) for c in cats if c["type"] == type_]
            cat_id = pick_from_list(f"{header} kategorileri:", cats_of_type, allow_none=True)
            amount = ask("Tutar: ")
            date_s = ask("Tarih (GG-AA-YYYY) [boş=bugün]: ")
            desc = ask("Açıklama (opsiyonel): ")
            try:
                tx = transaction_service.create_transaction(
                    user["user_id"], type_, amount, date_s, cat_id, desc
                )
                cname = transaction_service.get_category_name_by_id(user["user_id"], tx["category_id"]) or "(yok)"
                print(f"Eklendi: {tx['date']} | {tx['amount']:.2f} | {cname} | id={tx['transaction_id']}")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel == "2":
            rows = transaction_service.enumerate_transactions_for_edit(user["user_id"], type_)
            if not rows:
                print(f"Hiç {header.lower()} kaydı yok.")
                continue
            print_txn_table(rows)
            try:
                idx = int(ask("Silinecek kayıt numarası (#): "))
                if idx < 1 or idx > len(rows):
                    print("Geçersiz numara.")
                    continue
            except ValueError:
                print("Geçersiz numara.")
                continue
            ok = ask("Silmek istediğinize emin misiniz? (yes/no): ").lower()
            if ok not in ("y", "yes", "e", "evet"):
                print("İşlem iptal edildi.")
                continue
            txn_id = rows[idx - 1]["transaction_id"]
            try:
                transaction_service.delete_transaction_by_id(txn_id, user["user_id"])
                print("Kayıt silindi.")
            except ValueError as e:
                print(f"Hata: {e}")
            except Exception as e:
                print(f"Bilinmeyen Hata: {e}")

        elif sel == "3":
            rows = transaction_service.enumerate_transactions_for_edit(user["user_id"], type_)
            if not rows:
                print(f"Düzenlenecek {header.lower()} kaydı yok.")
                continue
            print_txn_table(rows)
            try:
                idx = int(ask("Düzenlenecek kayıt numarası (#): "))
                if idx < 1 or idx > len(rows):
                    print("Geçersiz numara.")
                    continue
            except ValueError:
                print("Geçersiz numara.")
                continue

            current = rows[idx - 1]
            temp_desc = current["description"]
            temp_cid = current["category_id"]
            temp_amt = f"{current['amount']:.2f}"

            while True:
                cname = transaction_service.get_category_name_by_id(user["user_id"], temp_cid) or "(yok)"
                print(f"""
Seçilen kayıt:
  Tarih: {current['date']}
  Tutar: {temp_amt}
  Kategori: {cname}  (id={temp_cid or "-"})
  Açıklama: {temp_desc}
""")
                field = choose_edit_field()
                if not field:
                    continue
                if field == "description":
                    temp_desc = ask("Yeni açıklama (boş bırakılabilir): ")
                elif field == "category_id":
                    cats = category_service.list_categories(user["user_id"])
                    cats_of_type = [(c["category_id"], c["name"]) for c in cats if c["type"] == type_]
                    sel_cid = pick_from_list(f"{header} kategorileri:", cats_of_type, allow_none=True)
                    temp_cid = sel_cid if sel_cid else None
                elif field == "amount":
                    temp_amt = ask("Yeni tutar: ")
                elif field == "commit":
                    try:
                        old_amt = f"{current['amount']:.2f}"
                        new_amt_f = transaction_service._parse_amount_no_try(temp_amt)
                        new_amt_s = f"{new_amt_f:.2f}"
                        if old_amt != new_amt_s:
                            transaction_service.update_transaction_by_index(user["user_id"], type_, idx, "amount", temp_amt)
                        if (current["category_id"] or None) != (temp_cid or None):
                            transaction_service.update_transaction_by_index(user["user_id"], type_, idx, "category_id", temp_cid or "")
                        if (current["description"] or "") != (temp_desc or ""):
                            transaction_service.update_transaction_by_index(user["user_id"], type_, idx, "description", temp_desc or "")
                        print("Değişiklikler kaydedildi.")
                    except ValueError as e:
                        print(f"Hata: {e}")
                        continue
                    except Exception as e:
                        print(f"Bilinmeyen Hata: {e}")
                        continue
                    break
                elif field == "cancel":
                    print("Değişiklikler kaydedilmedi (vazgeçildi).")
                    break

        elif sel == "4":
            rows = transaction_service.enumerate_transactions_for_edit(user["user_id"], type_)
            if not rows:
                print(f"Hiç {header.lower()} kaydı yok.")
                continue
            print_txn_table(rows)

        elif sel == "5":
            break
        else:
            print("Yanlış seçim.")


def reports_menu(user: dict) -> None:
    def ask_type_menu() -> str:
        while True:
            print("Tür seçin:\n  1) Gelir (income)\n  2) Gider (expense)\n")
            s = ask("Seçiminiz: ").strip()
            if s == "1":
                return "income"
            if s == "2":
                return "expense"
            print("Geçersiz seçim.")

    def ask_date(label: str) -> str:
        return ask(f"{label} (GG-AA-YYYY): ")

    while True:
        print("""RAPORLAR
  1) Genel Toplam (Tüm veriler)
  2) Haftalık (son 7 gün, bugün dahil)
  3) Aylık (içinde bulunulan ay)
  4) 12 Aylık Tablo (son 12 takvim ayı)
  5) Özel Aralık (başlangıç-bitiş dahil)
  6) Kategori Kırılımı (tür seç)
  7) Geri
""")
        sel = ask("Seçiminiz: ").strip()

        if sel == "1":
            s = report_service.totals_all(user["user_id"])
            print("\nGENEL TOPLAM")
            print(f"{'Gelir:':>10} {s['income']:>12.2f}")
            print(f"{'Gider:':>10} {s['expense']:>12.2f}")
            print(f"{'Bakiye:':>10} {s['net']:>12.2f}")

        elif sel == "2":
            s = report_service.weekly_summary(user["user_id"])
            print("\nSON 7 GÜN")
            print(f"{'Gelir:':>10} {s['income']:>12.2f}")
            print(f"{'Gider:':>10} {s['expense']:>12.2f}")
            print(f"{'Bakiye:':>10} {s['net']:>12.2f}")

        elif sel == "3":
            s = report_service.current_month_summary(user["user_id"])
            print("\nBU AY")
            print(f"{'Gelir:':>10} {s['income']:>12.2f}")
            print(f"{'Gider:':>10} {s['expense']:>12.2f}")
            print(f"{'Bakiye:':>10} {s['net']:>12.2f}")

        elif sel == "4":
            rows = report_service.last_12_months_table(user["user_id"])
            print("\nYYYY-AA        GELİR        GİDER       BAKİYE")
            print("------------------------------------------------")
            for r in rows:
                print(f"{r['period']:>7s} {r['income']:12.2f} {r['expense']:12.2f} {r['balance']:12.2f}")

        elif sel == "5":
            start = ask_date("Başlangıç")
            end = ask_date("Bitiş")
            try:
                s = report_service.range_summary(user["user_id"], start, end)
                print(f"\n{start} - {end}")
                print(f"{'Gelir:':>10} {s['income']:>12.2f}")
                print(f"{'Gider:':>10} {s['expense']:>12.2f}")
                print(f"{'Bakiye:':>10} {s['net']:>12.2f}")
            except ValueError as e:
                print(f"Hata: {e}")

        elif sel == "6":
            t = ask_type_menu()
            use_range = ask("Tarih aralığı ister misiniz? (yes/no): ").lower()
            if use_range in ("y", "yes", "e", "evet"):
                start = ask_date("Başlangıç")
                end = ask_date("Bitiş")
                try:
                    rows = report_service.by_category(user["user_id"], t, start, end)
                except ValueError as e:
                    print(f"Hata: {e}")
                    continue
            else:
                rows = report_service.by_category(user["user_id"], t)

            print(f"\nKATEGORİ BAZINDA TOPLAMLAR ({'Gelir' if t == 'income' else 'Gider'})")
            if not rows:
                print("(kayıt yok)")
            else:
                width = max(15, max(len((name or '').strip() or '(yok)') for name, _ in rows))
                for name, total in rows:
                    safe = (name or "").strip() or "(yok)"
                    print(f"{safe:<{width}} : {total:>12.2f}")

        elif sel == "7":
            break
        else:
            print("Yanlış seçim.")


def app_menu(user: dict) -> None:
    while True:
        print("""ANA MENÜ
  1) Gelir İşlemleri
  2) Gider İşlemleri
  3) Kategori Yönetimi
  4) Raporlar
  5) Hesap/oturum
  6) Çıkış
""")
        secim = ask("Seçiminiz: ").strip()
        if secim == "1":
            transaction_menu(user, "income")
        elif secim == "2":
            transaction_menu(user, "expense")
        elif secim == "3":
            category_menu(user)
        elif secim == "4":
            reports_menu(user)
        elif secim == "5":
            print("Hesap işlemleri oluşturulacak.")
        elif secim == "6":
            break
        else:
            print("Yanlış seçim.")
