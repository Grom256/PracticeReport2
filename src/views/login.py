import flet as ft

from models import AUTH_USER_ID_KEY, login_user
from .components import shell


def login_view(page):
    email = ft.TextField(label="Email", width=320)
    password = ft.TextField(label="Password", password=True, width=320)
    message = ft.Text()

    async def submit(e):
        user, text = login_user(email.value, password.value)
        message.value = text
        if user:
            page.current_user = user
            await page.prefs.set(AUTH_USER_ID_KEY, user["id"])
            await page.push_route("/")
        page.update()

    return shell(
        page,
        "/login",
        [
            ft.Text("Login", size=28, weight=ft.FontWeight.BOLD),
            email,
            password,
            ft.FilledButton("Login", on_click=submit),
            message,
        ],
    )
