import flet as ft

from models import ITEMS_PATH, ORDERS_PATH, load_json, save_json, update_order_status
from .components import shell


def admin_view(page):
    products = load_json(ITEMS_PATH)
    orders = load_json(ORDERS_PATH)
    rows = [ft.Text("Admin panel", size=28, weight=ft.FontWeight.BOLD), ft.Text("Stock")]

    for index, product in enumerate(products):
        qty = ft.TextField(value=str(product.get("qty", 0)), width=90)

        def save_qty(e, i=index, field=qty):
            products[i]["qty"] = int(field.value or 0)
            save_json(products, ITEMS_PATH)
            page.update()

        rows.append(ft.Row(controls=[ft.Text(product.get("name"), width=320), qty, ft.FilledButton("Save", on_click=save_qty)]))

    rows.append(ft.Text("Orders"))
    for order in orders:
        status = ft.Dropdown(value=order.get("status", "created"), width=160, options=[ft.dropdown.Option("created"), ft.dropdown.Option("paid"), ft.dropdown.Option("sent")])

        def save_status(e, order_id=order.get("id"), dropdown=status):
            update_order_status(order_id, dropdown.value)
            page.update()

        rows.append(ft.Row(controls=[ft.Text(f"Order #{order.get('id')}", width=160), status, ft.FilledButton("Update", on_click=save_status)]))

    return shell(page, "/admin", rows)
