import re

import bcrypt

from .storage_logic import USERS_PATH, load_json, next_numeric_id, save_json


DEFAULT_ADMIN_EMAIL = 'admin@pashacustom.com'


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False


def load_users():
    users = load_json(USERS_PATH)
    if not isinstance(users, list):
        users = []

    admin_exists = any(user.get('email') == DEFAULT_ADMIN_EMAIL for user in users)
    if not admin_exists:
        admin = {
            'id': 1,
            'name': 'Адмін',
            'surname': 'PashaCustom',
            'email': DEFAULT_ADMIN_EMAIL,
            'phone': '0000000000',
            'password': hash_password('admin123'),
            'is_admin': True,
        }
        users.insert(0, admin)
        save_json(users, USERS_PATH)
    return users


def find_user_by_email(email):
    normalized = (email or '').strip().lower()
    for user in load_users():
        if user.get('email', '').lower() == normalized:
            return user
    return None


def find_user_by_id(user_id):
    try:
        normalized_id = int(user_id)
    except (TypeError, ValueError):
        return None
    for user in load_users():
        if user.get('id') == normalized_id:
            return user
    return None


def get_public_user_by_id(user_id):
    user = find_user_by_id(user_id)
    return {key: value for key, value in user.items() if key != 'password'} if user else None


def register_user(name, surname, email, phone, password, password_confirmation):
    name = (name or '').strip()
    surname = (surname or '').strip()
    email = (email or '').strip().lower()
    phone = (phone or '').strip()
    password = (password or '').strip()
    password_confirmation = (password_confirmation or '').strip()

    if not name or not surname or not email or not phone or not password or not password_confirmation:
        return None, 'Заповніть усі поля.'
    if len(name) < 2:
        return None, "Ім'я занадто коротке."
    if len(surname) < 2:
        return None, 'Прізвище занадто коротке.'
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return None, 'Введіть коректний email.'

    phone_digits = ''.join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 10:
        return None, 'Введіть коректний номер телефону.'
    if len(password) < 8:
        return None, 'Пароль має містити щонайменше 8 символів.'
    if not any(ch.isupper() for ch in password):
        return None, 'Пароль має містити хоча б одну велику літеру.'
    if not any(ch.isdigit() for ch in password):
        return None, 'Пароль має містити хоча б одну цифру.'
    if password != password_confirmation:
        return None, 'Паролі не збігаються.'
    if find_user_by_email(email):
        return None, 'Користувач із таким email вже зареєстрований.'

    users = load_users()
    user = {
        'id': next_numeric_id(users),
        'name': name,
        'surname': surname,
        'email': email,
        'phone': phone_digits,
        'password': hash_password(password),
        'is_admin': False,
    }
    users.append(user)
    save_json(users, USERS_PATH)

    public_user = {key: value for key, value in user.items() if key != 'password'}
    return public_user, 'Реєстрація успішна. Тепер можна увійти в акаунт.'


def login_user(email, password):
    email = (email or '').strip().lower()
    password = (password or '').strip()

    if not email or not password:
        return None, 'Введіть email та пароль.'

    user = find_user_by_email(email)
    if not user or not check_password(password, user.get('password', '')):
        return None, 'Неправильний email або пароль.'

    public_user = {key: value for key, value in user.items() if key != 'password'}
    return public_user, f"Вітаємо, {public_user['name']}!"


def update_user_profile(user_id, new_name, new_surname, new_phone):
    new_name = (new_name or '').strip()
    new_surname = (new_surname or '').strip()
    new_phone = (new_phone or '').strip()

    if len(new_name) < 2:
        return None, "Ім'я занадто коротке."
    if len(new_surname) < 2:
        return None, 'Прізвище занадто коротке.'

    phone_digits = ''.join(ch for ch in new_phone if ch.isdigit())
    if len(phone_digits) < 10:
        return None, 'Введіть коректний номер телефону.'

    users = load_users()
    for user in users:
        if user.get('id') == int(user_id):
            user['name'] = new_name
            user['surname'] = new_surname
            user['phone'] = phone_digits
            save_json(users, USERS_PATH)
            public_user = {key: value for key, value in user.items() if key != 'password'}
            return public_user, 'Дані оновлено.'

    return None, 'Користувача не знайдено.'
