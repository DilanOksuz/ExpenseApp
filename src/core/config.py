from pathlib import Path

DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.txt"
CATEGORIES_FILE = DATA_DIR / "categories.txt"
TRANSACTIONS_FILE = DATA_DIR / "transactions.txt"


def ensure_data_files_exist() -> None:

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for p in (USERS_FILE, CATEGORIES_FILE, TRANSACTIONS_FILE):
        if not p.exists():
            p.write_text("", encoding="utf-8")