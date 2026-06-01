from datetime import datetime

from .storage_logic import ORDERS_PATH, load_json, next_numeric_id, save_json

ORDER_STATUSES = ['created', 'paid', 'processing', 'shipped', 'completed', 'cancelled']


def parse_price(price):
    try:
        return float(str(price).replace('$', '').strip() or 0)
    except ValueError:
        return 0


def calculate_total(items):
    total = 0
    for item in items:
        total += parse_price(item.get('price', 0)) * int(item.get('qty', 1))
    return round(total, 2)


def load_orders():
    orders = load_json(ORDERS_PATH)
    if not isinstance(orders, list):
        return []
    return orders


def get_user_orders(user):
    if not user:
        return []

    user_id = user.get('id')
    email = user.get('email')
    result = []

    for order in load_orders():
        order_user = order.get('user', {})
        if order_user.get('id') == user_id or order_user.get('email') == email:
            result.append(order)
    return result


def status_title(status):
    titles = {
        'created': 'Створено',
        'paid': 'Оплачено',
        'processing': 'В обробці',
        'shipped': 'Відправлено',
        'completed': 'Завершено',
        'cancelled': 'Скасовано',
    }
    return titles.get(status, status)


def validate_payment(payment_method, card_number='', card_expiry='', card_cvv='', card_holder='', paypal_email=''):
    if payment_method == 'card':
        if not card_holder.strip():
            return False, "Введіть ім'я власника картки."

        digits = ''.join(char for char in card_number if char.isdigit())
        if len(digits) < 13 or len(digits) > 19:
            return False, 'Введіть коректний номер банківської картки.'

        parts = card_expiry.strip().split('/')
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            return False, 'Введіть термін дії картки у форматі MM/YY.'

        month = int(parts[0])
        year = 2000 + int(parts[1])
        now = datetime.now()
        if month < 1 or month > 12:
            return False, 'Некоректний місяць.'
        if year < now.year or (year == now.year and month < now.month):
            return False, 'Термін дії картки закінчився.'

        cvv = card_cvv.strip()
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            return False, 'CVV має містити 3 або 4 цифри.'

        return True, 'Оплату карткою перевірено.'

    if payment_method == 'paypal':
        email = paypal_email.strip()
        if '@' not in email or '.' not in email:
            return False, 'Введіть коректний PayPal email.'
        return True, 'PayPal email перевірено.'

    return False, 'Оберіть спосіб оплати.'


def create_order(user, cart_items, payment_method, payment_details, delivery_address=None):
    orders = load_orders()
    order = {
        'id': next_numeric_id(orders),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user': {
            'id': user.get('id'),
            'name': user.get('name'),
            'surname': user.get('surname'),
            'email': user.get('email'),
            'phone': user.get('phone'),
        },
        'items': cart_items,
        'total': calculate_total(cart_items),
        'payment_method': payment_method,
        'payment_details': payment_details,
        'delivery_address': delivery_address or {},
        'status': 'created',
    }
    orders.append(order)
    save_json(orders, ORDERS_PATH)
    return order


def update_order_status(order_id, status):
    if status not in ORDER_STATUSES:
        return False

    orders = load_orders()
    for order in orders:
        if str(order.get('id')) == str(order_id):
            order['status'] = status
            save_json(orders, ORDERS_PATH)
            return True

    return False
