from fake_data.auth import authenticate_user
from fake_data.fake_api import get_user_profile
from fake_data.fake_memory import set_user_session

# Example: Login
user_id = input("Enter ID: ")
pw = input("Enter Password: ")

if authenticate_user(user_id, pw):
    print("✅ Authenticated")
    user_profile = get_user_profile(user_id)
    if user_profile:
        set_user_session(user_profile)
        print(f"Welcome, {user_profile['name']} ({user_profile['role']})")
    else:
        print("❌ User data not found")
else:
    print("❌ Invalid credentials")
