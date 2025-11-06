from src.core.config import USERS_FILE
from src.core.ids import new_id
from src.core.validation import validate_password, validate_username, normalize_username
from src.storage.txt_store import read_rows, append_row

def _username_exist(username: str) -> bool:
    norm = normalize_username(username)
    for row in read_rows(USERS_FILE):
        if len(row) < 3:
            continue
        _, uname, _ = row
        if normalize_username(uname) == norm:
            return True
            
    return False
       

def register(username: str, pw1: str, pw2: str):
    validate_username(username)
    validate_password(pw1)
    validate_password(pw2)

    if pw1 != pw2 :
        raise ValueError("Şifreler farklı")
    if _username_exist(username):
        raise ValueError("Bu kullanıcı adı zaten alınmış")

    uid = new_id()
    append_row(USERS_FILE, [uid , username.strip(), pw1])
    return{"user_id":uid , "username":username.strip()}


def login(user_name: str , password: str) -> dict:
    validate_username(user_name)
    validate_password(password)
    target = normalize_username(user_name)

    for row in read_rows(USERS_FILE):
        if len(row)<3:
            continue
        uid, uname, pw = row
        if normalize_username(uname) == target and pw==password:
            return {"user_id": uid , "username":uname}
    raise ValueError("Kullanıcı adı ve şifre hatalı. ")