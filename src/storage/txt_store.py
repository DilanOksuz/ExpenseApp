from pathlib import Path

SEP ="\t"
ENC = "utf-8"

def read_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return[]
    rows: list[list[str]] = []
    with path.open("r", encoding=ENC,newline="") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            rows.append(line.rstrip("\n").split(SEP))
    return rows

def append_row(path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding=ENC, newline="") as f:
        f.write(SEP.join(fields) + "\n")

