from src.core.config import ensure_data_files_exist
from src.ui.menu import welcome_loop, app_menu

def main():
    ensure_data_files_exist()

    user = welcome_loop()
    if not user:
        print("\nProgramdan çıkılıyor.")
        return

    app_menu(user)

    print("\nGörüşmek üzere.")

if __name__ == "__main__":
    main()
