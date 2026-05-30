import flet as ft

from .components import shell


def home_view(page):
    return shell(
        page,
        "/",
        [
            ft.Text("PashaCustomCorporation", size=34, weight=ft.FontWeight.BOLD),
            ft.Text("Early collectible shop prototype. The first version is intentionally rough."),
            ft.Image(src="hero.png", width=560, fit=ft.BoxFit.CONTAIN),
        ],
    )
