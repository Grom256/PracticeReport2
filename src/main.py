import os

import flet as ft

from models import AUTH_USER_ID_KEY, get_public_user_by_id
from models.storage_logic import ITEMS_PATH, load_json, save_json
from views import admin_view, cart_view, home_view, login_view, orders_view, product_view, regist_view, settings_view, shop_view


data = [
    {
        'name': 'Star Wars The Force Unleashed: StarKiller [Limited Edition]',
        'manufacturer': 'PashaCustomCorporation',
        'qty': 3,
        'price': '65',
        'image_src': 'starkiller.jpg'
    },
    {
        'name': 'Star Wars The Clone Wars: Umbaran Soldier',
        'manufacturer': 'PashaCustomCorporation',
        'qty': 152,
        'price': '40',
        'image_src': 'umbar.jpg'
    },
    {
        'name': 'Star Wars Episod 2: Queen of Nabu, Padme Amidala [Limited Edition]',
        'manufacturer': 'PashaCustomCorporation',
        'qty': 9,
        'price': '60',
        'image_src': 'padme.jpg'
    },
    {
        'name': 'Star Wars Episod 3: Clone of 104th battalion',
        'manufacturer': 'GrandPaCloneCustoms',
        'qty': 274,
        'price': '35',
        'image_src': 'clone_104.jpg'
    },
    {
        'name': 'Star Wars Episod 4: Bail Organa',
        'manufacturer': 'PashaCustomCorporation',
        'qty': 83,
        'price': '45',
        'image_src': 'organa.jpg'
    },
    {
        'name': 'Star Wars Jedi Fallen Order: Purge Trooper',
        'manufacturer': 'PashaCustomCorporation',
        'qty': 172,
        'price': '40',
        'image_src': 'jedi_hunter.jpg'
    },
]

if not load_json(ITEMS_PATH):
    save_json(data, ITEMS_PATH)


async def main(page: ft.Page):
    page.title = 'PashaCustomCorporation'
    page.prefs = ft.SharedPreferences()
    remembered_user_id = await page.prefs.get(AUTH_USER_ID_KEY)
    page.current_user = get_public_user_by_id(remembered_user_id)
    page.theme_mode = ft.ThemeMode.LIGHT

    page.cart = []

    async def route_change(e=None):
        page.views.clear()
        page.views.append(home_view(page))
        if page.route == '/settings':
            page.views.append(settings_view(page))
        elif page.route == '/shop':
            page.views.append(shop_view(page))
        elif page.route.startswith('/product/'):
            page.views.append(product_view(page))
        elif page.route == '/cart':
            page.views.append(cart_view(page))
        elif page.route == '/orders':
            page.views.append(orders_view(page))
        elif page.route == '/login':
            page.views.append(login_view(page))
        elif page.route == '/registration':
            page.views.append(regist_view(page))
        elif page.route == '/admin':
            page.views.append(admin_view(page))

        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    await route_change()


if __name__ == '__main__':
    ft.run(
        main,
        assets_dir='assets',
        view=ft.AppView.WEB_BROWSER,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8000)),
    )
