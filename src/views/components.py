import math
import flet as ft

GOLD = '#FFD700'
DARK = '#18233F'
SURFACE = '#F6F6F6'

BG_GRADIENT = ft.LinearGradient(
    begin=ft.Alignment.TOP_LEFT,
    end=ft.Alignment.BOTTOM_RIGHT,
    colors=['#FFE900', ft.Colors.GREY_300, '#000000'],
)




def page_bg():
    return ft.Container(
        expand=True,
        gradient=BG_GRADIENT,
    )


def footer_bar():
    return ft.BottomAppBar(
        height=52,
        bgcolor=DARK,
        padding=ft.Padding(left=18, top=8, right=18, bottom=8),
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                    controls=[
                        ft.Text('PashaCustomCorporation', color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            spacing=18,
                            controls=[
                                ft.Text('Email: support@pashacustom.com', color=ft.Colors.WHITE70, size=12),
                                ft.Text('Телефон: +380 50 111 22 33', color=ft.Colors.WHITE70, size=12),
                                ft.Text('Instagram: @pashacustomcorp', color=ft.Colors.WHITE70, size=12),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        'Розроблено та створено Victor Hadupiak',
                        color=ft.Colors.WHITE38,
                        size=10,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
            ],
        ),
    )


def main_appbar(page, current_route='/'):
    current_user = getattr(page, 'current_user', None)

    def make_handler(route):
        async def handler(e):
            await page.push_route(route)
        return handler

    tabs = [
        ('Головна', '/'),
        ('Магазин', '/shop'),
        ('Кошик', '/cart'),
        ('Мої замовлення', '/orders'),
        ('Налаштування', '/settings'),
    ]

    if current_user and current_user.get('is_admin'):
        tabs.append(('Адмін панель', '/admin'))

    if current_user:
        tabs.append((current_user['name'], '/settings'))
    else:
        tabs.append(('Увійти', '/login'))

    buttons = []
    for label, route in tabs:
        is_active = current_route == route
        buttons.append(
            ft.TextButton(
                label,
                style=ft.ButtonStyle(
                    color=DARK if is_active else ft.Colors.BLACK,
                    bgcolor=GOLD if is_active else ft.Colors.TRANSPARENT,
                ),
                on_click=make_handler(route),
            )
        )

    return ft.AppBar(
        title=ft.Text('PashaCustomCorporation', color=ft.Colors.BLACK),
        bgcolor=GOLD,
        actions=[ft.Row(controls=buttons)],
    )



def info_chip(icon, text, color=DARK):
    return ft.Container(
        padding=ft.Padding(left=10, top=6, right=10, bottom=6),
        border_radius=8,
        bgcolor='#FFFFFF',
        border=ft.border.all(1, '#E1E1E1'),
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(icon, size=16, color=color),
                ft.Text(text, size=12, color=ft.Colors.BLACK87),
            ],
        ),
    )
