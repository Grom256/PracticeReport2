import flet as ft

from models import ITEMS_PATH, load_json
from .components import GOLD, shell


def format_price(value):
    return f"${float(value):.2f}"


def shop_view(page):
    products = load_json(ITEMS_PATH)

    def card(index, product):
        async def open_product(e):
            await page.push_route(f"/product/{index}")

        async def add_to_cart(e):
            if not hasattr(page, "cart"):
                page.cart = []
            page.cart.append({"product_index": index, "qty": 1})
            page.update()

        buttons = [ft.OutlinedButton("Details", on_click=open_product)]
        try:
            from .cart import cart_view  # noqa: F401
            buttons.append(ft.FilledButton("Add", on_click=add_to_cart))
        except ImportError:
            pass

        return ft.Container(
            width=260,
            padding=12,
            border_radius=8,
            bgcolor="#1a1a2e",
            content=ft.Column(
                controls=[
                    ft.Image(src=product.get("image_src", ""), height=140, fit=ft.BoxFit.CONTAIN),
                    ft.Text(product.get("name", "Product"), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(format_price(product.get("price", 0)), color=GOLD),
                    ft.Row(controls=buttons),
                ],
            ),
        )

    return shell(
        page,
        "/shop",
        [
            ft.Text("Catalog draft", size=28, weight=ft.FontWeight.BOLD),
            ft.Row(wrap=True, controls=[card(i, product) for i, product in enumerate(products)]),
        ],
    )
