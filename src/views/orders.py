import flet as ft

from models import get_user_orders
from .components import shell
from .shop import format_price


def orders_view(page):
    orders = get_user_orders(getattr(page, "current_user", None))
    rows = []
    for order in orders:
        rows.append(
            ft.Container(
                padding=12,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                content=ft.Column(
                    controls=[
                        ft.Text(f"Order #{order.get('id')}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Total: {format_price(order.get('total', 0))}"),
                        ft.Text(f"Status: {order.get('status')}"),
                    ]
                ),
            )
        )
    if not rows:
        rows.append(ft.Text("No orders yet."))
    return shell(page, "/orders", [ft.Text("Orders", size=28), *rows])
