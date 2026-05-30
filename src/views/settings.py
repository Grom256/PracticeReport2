import flet as ft

from models import AUTH_USER_ID_KEY, update_user_profile
from .components import shell


def settings_view(page):
    current_user = getattr(page, "current_user", None)
    if not current_user:
        return shell(page, "/settings", [ft.Text("Settings"), ft.Text("Login to edit profile.")])

    name = ft.TextField(label="Name", value=current_user.get("name", ""), width=320)
    message = ft.Text()

    async def save(e):
        user, text = update_user_profile(current_user["id"], name.value)
        message.value = text
        if user:
            page.current_user = user
        page.update()

    async def logout(e):
        page.current_user = None
        await page.prefs.remove(AUTH_USER_ID_KEY)
        await page.push_route("/")

    return shell(page, "/settings", [ft.Text("Profile settings", size=28), name, ft.FilledButton("Save", on_click=save), ft.OutlinedButton("Logout", on_click=logout), message])
