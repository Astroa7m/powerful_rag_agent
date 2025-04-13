import json

def get_user_profile(user_id: str, data_file="fake_users_info.json") -> dict | None:
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        for user in data["users"]:
            if str(user["id"]) ==user_id:
                return user
    return None