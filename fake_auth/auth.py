def authenticate_user(user_id: str, password: str, credentials_file="users.txt") -> bool:
    with open(credentials_file, "r") as file:
        for line in file:
            stored_id, stored_pw = line.strip().split(":")
            if user_id == stored_id and password == stored_pw:
                return True
    return False