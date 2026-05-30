import flet as ft

GOLD = "#FFD700"
DARK = "#18233F"
PANEL = "#C7C7C7"


def nav_button(page, label, route):
    async def go(e):
        await page.push_route(route)

    return ft.TextButton(label, on_click=go)


def appbar(page, current_route="/"):
    routes = [
        ("Home", "/"),
        ("Shop", "/shop"),
        ("Cart", "/cart"),
        ("Orders", "/orders"),
        ("Settings", "/settings"),
    ]
    if getattr(page, "current_user", None) and page.current_user.get("is_admin"):
        routes.append(("Admin", "/admin"))
    return ft.AppBar(
        title=ft.Text("PashaCustomCorporation"),
        bgcolor=GOLD,
        actions=[ft.Row(controls=[nav_button(page, label, route) for label, route in routes])],
    )


def footer():
    return ft.BottomAppBar(
        height=48,
        bgcolor=DARK,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.Text("support@pashacustom.com", color=ft.Colors.WHITE70, size=12)],
        ),
    )


def shell(page, route, controls):
    return ft.View(
        route=route,
        padding=24,
        appbar=appbar(page, route),
        bottom_appbar=footer(),
        bgcolor=PANEL,
        scroll=ft.ScrollMode.AUTO,
        controls=controls,
    )
