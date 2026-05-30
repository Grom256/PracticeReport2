import flet as ft

try:
    from models import AUTH_USER_ID_KEY, get_public_user_by_id
except ImportError:
    AUTH_USER_ID_KEY = None
    get_public_user_by_id = None

from views import available_views, home_view


async def main(page: ft.Page):
    page.title = "PashaCustomCorporation"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.cart = []

    if AUTH_USER_ID_KEY:
        page.prefs = ft.SharedPreferences()
        remembered_user_id = await page.prefs.get(AUTH_USER_ID_KEY)
        page.current_user = get_public_user_by_id(remembered_user_id)
    else:
        page.current_user = None

    async def route_change(e=None):
        page.views.clear()
        page.views.append(home_view(page))
        route = page.route or "/"
        view_factory = available_views().get(route)

        if route.startswith("/product/"):
            view_factory = available_views().get("/product")

        if view_factory and route != "/":
            page.views.append(view_factory(page))

        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    await route_change()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=64108)
