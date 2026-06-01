import flet as ft

from models import AUTH_USER_ID_KEY, update_user_profile
from views.components import GOLD, footer_bar, info_chip, main_appbar


def settings_view(page):
    async def go_to_login(e):
        await page.push_route('/login')

    async def logout(e):
        page.current_user = None
        page.cart = []
        await page.prefs.remove(AUTH_USER_ID_KEY)
        await page.push_route('/')

    current_user = getattr(page, 'current_user', None)

    if current_user:
        name_input = ft.TextField(label="Ім'я", value=current_user.get('name', ''), width=300)
        surname_input = ft.TextField(label='Прізвище', value=current_user.get('surname', ''), width=300)
        phone_input = ft.TextField(label='Номер телефону', value=current_user.get('phone', ''), width=300)
        profile_message = ft.Text(visible=False, size=13)

        async def save_profile(e):
            updated_user, text = update_user_profile(
                current_user['id'],
                name_input.value,
                surname_input.value,
                phone_input.value,
            )
            profile_message.value = text
            profile_message.color = ft.Colors.GREEN if updated_user else ft.Colors.RED
            profile_message.visible = True
            if updated_user:
                page.current_user = updated_user
            page.update()

        content = ft.Column(
            spacing=16,
            expand=True,
            controls=[
                ft.Text('Профіль користувача', size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    spacing=10,
                    controls=[
                        info_chip(ft.Icons.EMAIL, current_user.get('email', '')),
                        info_chip(
                            ft.Icons.SHIELD if current_user.get('is_admin') else ft.Icons.PERSON,
                            'Адміністратор' if current_user.get('is_admin') else 'Користувач',
                        ),
                    ],
                ),
                ft.Divider(),
                ft.Text('Редагувати дані', size=20, weight=ft.FontWeight.BOLD),
                ft.Text('Email змінити не можна.', size=13),
                name_input,
                surname_input,
                phone_input,
                profile_message,
                ft.FilledButton('Зберегти зміни', icon=ft.Icons.SAVE, on_click=save_profile),
                ft.Divider(),
                ft.OutlinedButton('Вийти з акаунта', icon=ft.Icons.LOGOUT, on_click=logout),
            ],
        )
    else:
        content = ft.Column(
            spacing=16,
            expand=True,
            controls=[
                ft.Text('Налаштування', size=24, weight=ft.FontWeight.BOLD),
                ft.Text('Увійдіть, щоб бачити контактні дані та редагувати профіль.', size=16),
                ft.FilledButton('Увійти', icon=ft.Icons.LOGIN, on_click=go_to_login),
            ],
        )

    return ft.View(
        route='/settings',
        scroll=ft.ScrollMode.AUTO,
        bgcolor='#C7C7C7',
        appbar=main_appbar(page, '/settings'),
        bottom_appbar=footer_bar(),
        controls=[
            ft.Container(
                padding=32,
                content=content,
            ),

        ],
    )
