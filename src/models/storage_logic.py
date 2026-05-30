import json
from pathlib import Path

STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage"
USERS_PATH = STORAGE_DIR / "users.json"
ITEMS_PATH = STORAGE_DIR / "items.json"
ORDERS_PATH = STORAGE_DIR / "orders.json"
AUTH_USER_ID_KEY = "pasha_custom_auth_user_id"


def load_json(path, default=None):
    if default is None:
        default = []
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8") or "[]")
    except json.JSONDecodeError:
        return default


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def next_id(records):
    return max([int(item.get("id", 0)) for item in records] or [0]) + 1
