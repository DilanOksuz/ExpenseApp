from src.core.config import ensure_data_files_exist
from src.ui.menu import register_flow


def main():
    ensure_data_files_exist()
    register_flow()


if __name__ == "__main__":
    main()