import flet as ft

from models import ITEMS_PATH, load_json
from .components import GOLD, shell
from .shop import format_price


def product_view(page):
    products = load_json(ITEMS_PATH)
    try:
        index = int((page.route or "").split("/")[-1])
        product = products[index]
    except (ValueError, IndexError):
        product = {}

    return shell(
        page,
        page.route,
        [
            ft.Text(product.get("name", "Product not found"), size=28, weight=ft.FontWeight.BOLD),
            ft.Image(src=product.get("image_src", ""), width=360, fit=ft.BoxFit.CONTAIN),
            ft.Text(f"Manufacturer: {product.get('manufacturer', 'Unknown')}"),
            ft.Text(f"Available: {product.get('qty', 0)}"),
            ft.Text(format_price(product.get("price", 0)), size=24, color=GOLD),
        ],
    )
