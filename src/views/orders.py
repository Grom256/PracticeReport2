import flet as ft

from models import get_user_orders, status_title
from views.components import footer_bar, info_chip, main_appbar
from views.shop import format_price

LIGHT_BG = '#C7C7C7'
CARD_BG = '#FFFFFF'
DARK_GOLD = '#B8860B'


def payment_method_title(method):
    if method == 'card':
        return 'Банківська картка'
    if method == 'paypal':
        return 'PayPal'
    return method


def order_card(order):
    item_controls = []
    for item in order.get('items', []):
        item_controls.append(
            ft.Text(
                f"{item.get('name', 'Товар')} — {item.get('qty', 1)} шт. x {format_price(item.get('price', 0))}",
                size=14,
                color=ft.Colors.BLACK54,
            )
        )

    # Delivery address block (only if stored)
    delivery = order.get('delivery_address') or {}
    delivery_controls = []
    if delivery:
        addr_parts = [
            delivery.get('country', ''),
            delivery.get('city', ''),
            delivery.get('address', ''),
            delivery.get('postal', ''),
        ]
        addr_str = ', '.join(p for p in addr_parts if p)
        delivery_controls = [
            ft.Divider(color=ft.Colors.BLACK12),
            ft.Row(
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.LOCAL_SHIPPING, size=15, color=ft.Colors.BLACK45),
                    ft.Text(addr_str, size=13, color=ft.Colors.BLACK54),
                ],
            ),
        ]

    return ft.Container(
        padding=16,
        border_radius=8,
        bgcolor=CARD_BG,
        border=ft.border.all(1, '#CCCCCC'),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    f"Замовлення #{order.get('id', '')}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                ),
                ft.Text(f"Дата: {order.get('created_at', '')}", color=ft.Colors.BLACK54),
                ft.Text(
                    f"Спосіб оплати: {payment_method_title(order.get('payment_method', ''))}",
                    color=ft.Colors.BLACK54,
                ),
                ft.Text(
                    f"Сума: {format_price(order.get('total', 0))}",
                    weight=ft.FontWeight.BOLD,
                    color=DARK_GOLD,
                ),
                ft.Text(
                    f"Статус: {status_title(order.get('status', ''))}",
                    color=ft.Colors.BLACK54,
                ),
                ft.Divider(color=ft.Colors.BLACK12),
                *item_controls,
                *delivery_controls,
            ],
        ),
    )


def orders_view(page):
    current_user = getattr(page, 'current_user', None)

    async def go_to_login(e):
        await page.push_route('/login')

    if not current_user:
        content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Text(
                    'Щоб переглянути історію замовлень, потрібно увійти в акаунт.',
                    size=18,
                    color=ft.Colors.BLACK,
                ),
                ft.FilledButton('Увійти', icon=ft.Icons.LOGIN, on_click=go_to_login),
            ],
        )
    else:
        orders = get_user_orders(current_user)
        if not orders:
            content = ft.Text('У вас поки немає замовлень.', size=18, color=ft.Colors.BLACK)
        else:
            content = ft.Column(
                spacing=14,
                controls=[order_card(order) for order in reversed(orders)],
            )

    return ft.View(
        route='/orders',
        scroll=ft.ScrollMode.AUTO,
        bgcolor=LIGHT_BG,
        appbar=main_appbar(page, '/orders'),
        bottom_appbar=footer_bar(),
        controls=[
            ft.Container(
                expand=True,
                padding=24,
                content=content,
            ),
        ],
    )
