import flet as ft

from models import ITEMS_PATH, load_json
from .components import shell
from .shop import format_price


def cart_items(page):
    products = load_json(ITEMS_PATH)
    result = []
    for item in getattr(page, "cart", []):
        index = item.get("product_index")
        if index is not None and 0 <= index < len(products):
            result.append((products[index], item.get("qty", 1)))
    return result


def cart_view(page):
    rows = []
    total = 0
    for product, qty in cart_items(page):
        total += float(product.get("price", 0)) * qty
        rows.append(ft.Text(f"{product.get('name')} x {qty} - {format_price(product.get('price', 0))}"))

    if not rows:
        rows.append(ft.Text("Cart is empty."))

    try:
        from models import create_order

        async def checkout(e):
            order = create_order(getattr(page, "current_user", None), cart_items(page))
            page.cart = []
            page.snack_bar = ft.SnackBar(ft.Text(f"Order #{order['id']} created"))
            page.snack_bar.open = True
            page.update()

        rows.append(ft.FilledButton("Checkout", on_click=checkout))
    except ImportError:
        pass

    rows.append(ft.Text(f"Total: {format_price(total)}", size=20, weight=ft.FontWeight.BOLD))
    return shell(page, "/cart", [ft.Text("Cart", size=28, weight=ft.FontWeight.BOLD), *rows])
