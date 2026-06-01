import flet as ft

from models import AUTH_USER_ID_KEY, register_user
from views.components import BG_GRADIENT, footer_bar, main_appbar


def regist_view(page):
    name_input = ft.TextField(label="Ім'я", autofocus=True)
    surname_input = ft.TextField(label='Прізвище')
    email_input = ft.TextField(label='Email', keyboard_type=ft.KeyboardType.EMAIL)
    phone_input = ft.TextField(label='Номер телефону', keyboard_type=ft.KeyboardType.PHONE)
    password_input = ft.TextField(label='Пароль', password=True, can_reveal_password=True)
    password_confirmation_input = ft.TextField(label='Підтвердження пароля', password=True, can_reveal_password=True)
    message = ft.Text(visible=False)

    async def go_to_login(e):
        await page.push_route('/login')

    async def submit_registration(e):
        user, text = register_user(
            name_input.value,
            surname_input.value,
            email_input.value,
            phone_input.value,
            password_input.value,
            password_confirmation_input.value,
        )

        message.value = text
        message.color = ft.Colors.GREEN if user else ft.Colors.RED
        message.visible = True

        if user:
            page.current_user = user
            await page.prefs.set(AUTH_USER_ID_KEY, user['id'])
            name_input.value = ''
            surname_input.value = ''
            email_input.value = ''
            phone_input.value = ''
            password_input.value = ''
            password_confirmation_input.value = ''

        page.update()

    return ft.View(
        expand=True,
        padding = 0,
        route='/registration',
        appbar=main_appbar(page, '/registration'),
        bottom_appbar=footer_bar(),
        controls=[
            ft.Container(
                expand=True,
                gradient=BG_GRADIENT,
                padding=24,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    width=460,
                    spacing=14,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text('Створення акаунта', size=24, weight=ft.FontWeight.BOLD),
                        ft.Text('Пароль: мінімум 8 символів, велика літера і цифра.', size=13),
                        name_input,
                        surname_input,
                        email_input,
                        phone_input,
                        password_input,
                        password_confirmation_input,
                        message,
                        ft.FilledButton('Зареєструватися', icon=ft.Icons.PERSON_ADD, on_click=submit_registration),
                        ft.TextButton('Я вже маю акаунт', on_click=go_to_login),
                    ],
                ),
            ),
        ],
    )
