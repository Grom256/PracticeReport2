import flet as ft

from models import ITEMS_PATH, load_json
from views.cart import add_product_to_cart
from views.components import GOLD, footer_bar, info_chip, main_appbar, BG_GRADIENT
from views.shop import format_price


def get_product_index(route):
    try:
        return int(route.split('/')[-1])
    except ValueError:
        return None


def product_view(page):
    async def go_to_shop(e):
        await page.push_route('/shop')

    products = load_json(ITEMS_PATH)
    product_index = get_product_index(page.route)

    if product_index is None or product_index < 0 or product_index >= len(products):
        return ft.View(
            route=page.route,
            bottom_appbar=footer_bar(),
            appbar=main_appbar(page, page.route),
            controls=[
                ft.Container(
                    expand=True,
                    gradient=BG_GRADIENT,
                    padding=32,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text('Товар не знайдено.', size=22, weight=ft.FontWeight.BOLD),
                            ft.FilledButton('Повернутися до каталогу', on_click=go_to_shop),
                        ],
                    ),
                ),
            ],
        )

    product = products[product_index]
    product_name = product.get('name', 'Товар без назви')
    qty = int(product.get('qty', 0))
    message = ft.Text(visible=False)

    async def add_to_cart(e):
        success, text = add_product_to_cart(page, product_index)
        message.value = text
        message.color = ft.Colors.GREEN if success else ft.Colors.RED
        message.visible = True
        page.update()

    async def open_product(e, idx):
        await page.push_route(f'/product/{idx}')

    # Інші товари (виключаємо поточний)
    other_products = [
        (i, p) for i, p in enumerate(products)
        if i != product_index
    ][:4]

    other_cards = []
    for i, p in other_products:
        idx = i

        async def on_click(e, idx=idx):
            await page.push_route(f'/product/{idx}')

        other_cards.append(
            ft.Container(
                width=180,
                padding=10,
                border_radius=8,
                bgcolor='#1E1E24',
                on_click=on_click,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Image(src=p.get('image_src', ''), width=120, height=120, fit=ft.BoxFit.CONTAIN),
                        ft.Text(
                            p.get('name', ''),
                            size=12,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(format_price(p.get('price', 0)), size=13, color=GOLD, weight=ft.FontWeight.BOLD),
                    ],
                ),
            )
        )

    return ft.View(
        route=page.route,
        scroll=ft.ScrollMode.AUTO,
        padding=0,

        appbar=main_appbar(page, page.route),
        controls=[
            ft.Container(
            gradient=BG_GRADIENT,
                padding=32,
                content=ft.Column(
                    spacing=32,
                    controls=[
                        ft.Row(
                            spacing=32,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(
                                    width=360,
                                    height=360,
                                    bgcolor='#151518',
                                    border_radius=8,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Image(
                                        src=product.get('image_src', ''),
                                        fit=ft.BoxFit.CONTAIN,
                                        border_radius=8,
                                    ),
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Column(
                                        spacing=14,
                                        controls=[
                                            ft.Text(product_name, size=28, weight=ft.FontWeight.BOLD),
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    info_chip(ft.Icons.FACTORY, product.get('manufacturer', 'Невідомо')),
                                                    info_chip(ft.Icons.INVENTORY, f'Залишок: {qty}'),
                                                ],
                                            ),
                                            ft.Text(
                                                format_price(product.get('price', 0)),
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                                color='#D4A900',
                                            ),
                                            ft.Text(
                                                'Кастомна колекційна фігурка для фанатів LEGO-сумісних наборів.',
                                                size=16,
                                            ),
                                            ft.FilledButton(
                                                'Додати в кошик',
                                                icon=ft.Icons.SHOPPING_CART,
                                                disabled=qty <= 0,
                                                style=ft.ButtonStyle(
                                                    color=ft.Colors.BLACK,
                                                    bgcolor=GOLD,
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                ),
                                                width=220,
                                                on_click=add_to_cart,
                                            ),
                                            message,
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        ft.Divider(),
                        ft.Text('Інші товари', size=20, weight=ft.FontWeight.BOLD),
                        ft.Row(spacing=16, controls=other_cards),
                    ],
                ),
            ),
            footer_bar(),
        ],
    )