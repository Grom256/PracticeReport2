import flet as ft

from models import AUTH_USER_ID_KEY, login_user
from views.components import BG_GRADIENT, footer_bar, main_appbar


def login_view(page):
    email_input = ft.TextField(label='Email', keyboard_type=ft.KeyboardType.EMAIL, autofocus=True)
    password_input = ft.TextField(label='Пароль', password=True, can_reveal_password=True)
    message = ft.Text(visible=False)

    async def go_to_registration(e):
        await page.push_route('/registration')

    async def submit_login(e):
        user, text = login_user(email_input.value, password_input.value)
        message.value = text
        message.color = ft.Colors.GREEN if user else ft.Colors.RED
        message.visible = True

        if user:
            page.current_user = user
            await page.prefs.set(AUTH_USER_ID_KEY, user['id'])
            page.update()
            await page.push_route('/')
            return

        page.update()

    return ft.View(
        route='/login',
        padding = 0,
        appbar=main_appbar(page, '/login'),
        bottom_appbar=footer_bar(),
        controls=[
            ft.Container(
                gradient=BG_GRADIENT,
                expand=True,
                padding=24,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    width=420,
                    spacing=16,
                    controls=[
                        ft.Text('Увійдіть у PashaCustomCorporation', size=24, weight=ft.FontWeight.BOLD),
                        ft.Text('Після входу можна оформлювати замовлення та переглядати історію покупок.', size=14),
                        email_input,
                        password_input,
                        message,
                        ft.FilledButton('Увійти', icon=ft.Icons.LOGIN, on_click=submit_login),
                        ft.TextButton('Створити новий акаунт', on_click=go_to_registration),
                    ],
                ),
            ),
        ],
    )
