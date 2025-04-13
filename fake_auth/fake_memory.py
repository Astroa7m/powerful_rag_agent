session_data = {}

def set_user_session(user_profile: dict):
    global session_data
    session_data = user_profile

def get_user_session() -> dict:
    return session_data
