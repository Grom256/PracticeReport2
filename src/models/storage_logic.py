import json
import os

STORAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'storage')
USERS_PATH = os.path.join(STORAGE_DIR, 'users.json')
ITEMS_PATH = os.path.join(STORAGE_DIR, 'items.json')
ORDERS_PATH = os.path.join(STORAGE_DIR, 'orders.json')
AUTH_USER_ID_KEY = 'pasha_custom_auth_user_id'



def ensure_storage_dir():
    os.makedirs(STORAGE_DIR, exist_ok=True)


def save_json(data, path):
    ensure_storage_dir()
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f'Помилка збереження файлу {path}: {error}')


def load_json(path, default=None):
    if default is None:
        default = []

    if not os.path.exists(path):
        return default

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f'Помилка читання файлу {path}: {error}')
        return default


def next_numeric_id(records):
    biggest_id = 0
    for record in records:
        try:
            biggest_id = max(biggest_id, int(record.get('id', 0)))
        except (TypeError, ValueError):
            continue
    return biggest_id + 1
