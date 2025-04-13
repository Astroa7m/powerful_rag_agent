import os


def authenticate_user(user_id: str, password: str, credentials_file="users.txt") -> bool:
    BASE_DIR = os.path.dirname(__file__)
    CREDENTIALS_FILE = os.path.join(BASE_DIR, credentials_file)

    with open(CREDENTIALS_FILE, "r") as file:
        for line in file:
            stored_id, stored_pw = line.strip().split(":")
            if user_id == stored_id and password == stored_pw:
                return True
    return False
