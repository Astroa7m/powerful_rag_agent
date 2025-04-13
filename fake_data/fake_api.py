import json
import os


def get_user_profile(user_id: str, data_file="fake_users_info.json") -> dict | None:
    BASE_DIR = os.path.dirname(__file__)
    USER_INFO_FILE = os.path.join(BASE_DIR, data_file)
    with open(USER_INFO_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
        for user in data["users"]:
            if str(user["id"]) ==user_id:
                return user
    return None