import flet as ft

from models import AUTH_USER_ID_KEY, register_user
from .components import shell


def regist_view(page):
    name = ft.TextField(label="Name", width=320)
    email = ft.TextField(label="Email", width=320)
    password = ft.TextField(label="Password", password=True, width=320)
    message = ft.Text()

    async def submit(e):
        user, text = register_user(email.value, password.value, name.value)
        message.value = text
        if user:
            page.current_user = user
            await page.prefs.set(AUTH_USER_ID_KEY, user["id"])
            await page.push_route("/")
        page.update()

    return shell(page, "/registration", [ft.Text("Registration", size=28), name, email, password, ft.FilledButton("Create account", on_click=submit), message])
