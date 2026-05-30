from .storage_logic import USERS_PATH, load_json, next_id, save_json


def register_user(email, password, name=""):
    users = load_json(USERS_PATH)
    if any(user.get("email") == email for user in users):
        return None, "Email already exists."
    user = {"id": next_id(users), "email": email, "password": password, "name": name, "is_admin": email == "admin@admin.com"}
    users.append(user)
    save_json(users, USERS_PATH)
    return public_user(user), "Registered."


def login_user(email, password):
    for user in load_json(USERS_PATH):
        if user.get("email") == email and user.get("password") == password:
            return public_user(user), "Logged in."
    return None, "Wrong email or password."


def get_public_user_by_id(user_id):
    if not user_id:
        return None
    for user in load_json(USERS_PATH):
        if str(user.get("id")) == str(user_id):
            return public_user(user)
    return None


def update_user_profile(user_id, name):
    users = load_json(USERS_PATH)
    for user in users:
        if str(user.get("id")) == str(user_id):
            user["name"] = name
            save_json(users, USERS_PATH)
            return public_user(user), "Saved."
    return None, "User not found."


def public_user(user):
    return {key: value for key, value in user.items() if key != "password"}
