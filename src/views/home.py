import flet as ft

from .components import DARK, GOLD, footer_bar, main_appbar


def promo_card(title, text, icon):
    return ft.Container(
        expand=True,
        padding=18,
        border_radius=8,
        bgcolor='#F6F6F6',
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(icon, color='#D4A900', size=28),
                ft.Column(
                    spacing=6,
                    expand=True,
                    controls=[
                        ft.Text(title, size=17, weight=ft.FontWeight.BOLD),
                        ft.Text(text, size=14, color=ft.Colors.BLACK87),
                    ],
                ),
            ],
        ),
    )


def home_view(page):
    async def go_to_settings(e):
        await page.push_route('/settings')

    async def go_to_shop(e):
        await page.push_route('/shop')

    async def go_to_login(e):
        await page.push_route('/login')

    async def go_to_cart(e):
        await page.push_route('/cart')

    async def go_to_orders(e):
        await page.push_route('/orders')

    async def go_to_admin(e):
        await page.push_route('/admin')

    hero_section = ft.Container(

        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Image(
                    src="hero.png",

                    fit=ft.BoxFit.COVER,
                    expand=True

                ),

                ft.Container(
                    padding=48,
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=ft.Column(
                        width=540,
                        spacing=18,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "PashaCustomCorporation",
                                size=42,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                "Кастомні фігурки для колекцій, подарунків і фанатських наборів.",
                                size=19,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.FilledButton(
                                        "Перейти до каталогу",
                                        icon=ft.Icons.STORE,
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.BLACK,
                                            bgcolor="#FFD700",
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=go_to_shop,
                                    ),
                                    ft.OutlinedButton(
                                        "Мої замовлення",
                                        icon=ft.Icons.HISTORY,
                                        style=ft.ButtonStyle(color=ft.Colors.WHITE),
                                        on_click=go_to_orders,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    promo_section = ft.Container(
        padding=32,
        bgcolor=GOLD,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=8,
                    expand=True,
                    controls=[
                        ft.Text('Акція для колекціонерів Star Wars', size=16, weight=ft.FontWeight.BOLD),
                        ft.Text('Подарунок до замовлення від $100', size=28, weight=ft.FontWeight.BOLD),
                        ft.Text('До кожного великого замовлення додаємо фірмовий магніт і пріоритетне пакування.', size=15),
                    ],
                ),
                ft.FilledButton(
                    'Дивитися товари',
                    icon=ft.Icons.LOCAL_OFFER,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=DARK,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=go_to_shop,
                ),
            ],
        ),
    )

    info_section = ft.Container(
        padding=32,
        content=ft.Column(
            spacing=22,
            controls=[
                ft.Text('Чому обирають нас', size=26, weight=ft.FontWeight.BOLD),
                ft.Row(
                    spacing=16,
                    controls=[
                        promo_card(
                            'Баланс деталізації',
                            'Кожна фігурка зберігає стиль LEGO-сумісних наборів і впізнаваність персонажа.',
                            ft.Icons.BRUSH,
                        ),
                        promo_card(
                            'Обмежені партії',
                            'Лімітовані випуски мають власну цінність для колекціонерів і фанатів серій.',
                            ft.Icons.STAR,
                        ),
                        promo_card(
                            'Контроль замовлень',
                            'Користувач бачить історію покупок, статус і склад кожного замовлення.',
                            ft.Icons.RECEIPT_LONG,
                        ),
                    ],
                ),
            ],
        ),
    )

    return ft.View(
        route='/',
        padding=0,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        appbar=main_appbar(page, '/'),
        controls=[
            hero_section,
            promo_section,
            info_section,
            footer_bar(),
        ],
    )
