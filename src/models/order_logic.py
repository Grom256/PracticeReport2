from .storage_logic import ORDERS_PATH, load_json, next_id, save_json


def create_order(user, cart_items):
    orders = load_json(ORDERS_PATH)
    total = sum(float(product.get("price", 0)) * qty for product, qty in cart_items)
    order = {
        "id": next_id(orders),
        "user": user or {"email": "guest"},
        "items": [{"name": product.get("name"), "qty": qty, "price": product.get("price")} for product, qty in cart_items],
        "total": round(total, 2),
        "status": "created",
    }
    orders.append(order)
    save_json(orders, ORDERS_PATH)
    return order


def get_user_orders(user):
    orders = load_json(ORDERS_PATH)
    if not user:
        return orders
    return [order for order in orders if order.get("user", {}).get("id") == user.get("id")]


def update_order_status(order_id, status):
    orders = load_json(ORDERS_PATH)
    for order in orders:
        if str(order.get("id")) == str(order_id):
            order["status"] = status
    save_json(orders, ORDERS_PATH)
