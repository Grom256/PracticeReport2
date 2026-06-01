import os
import shutil

import flet as ft

from models import (
    ITEMS_PATH,
    ORDER_STATUSES,
    load_json,
    load_orders,
    load_users,
    save_json,
    status_title,
    update_order_status,
)
from views.components import DARK, GOLD, footer_bar, info_chip, main_appbar, BG_GRADIENT
from views.shop import format_price


def admin_view(page):
    async def go_home(e):
        await page.push_route('/')

    current_user = getattr(page, 'current_user', None)
    if not current_user or not current_user.get('is_admin'):
        return ft.View(
            route='/admin',
            bottom_appbar=footer_bar(),
            appbar=main_appbar(page, '/admin'),
            controls=[
                ft.Container(
                    expand=True,
                    gradient=BG_GRADIENT,
                    padding=32,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.LOCK, size=48, color=ft.Colors.RED),
                            ft.Text('Доступ дозволено тільки адміністратору.', size=20, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
            ],
        )

    selected_image = {'path': None, 'name': None, 'bytes': None}

    name_input = ft.TextField(label='Назва товару', width=400)
    manufacturer_input = ft.TextField(label='Виробник', width=400, value='PashaCustomCorporation')
    price_input = ft.TextField(label='Ціна ($)', width=190, keyboard_type=ft.KeyboardType.NUMBER)
    qty_input = ft.TextField(label='Кількість', width=190, keyboard_type=ft.KeyboardType.NUMBER)
    image_label = ft.Text('Зображення не вибрано', color=ft.Colors.RED)
    message = ft.Text(visible=False)
    status_message = ft.Text(visible=False, size=13)
    products_list = ft.Column(spacing=10)
    orders_list = ft.Column(spacing=10)

    file_picker = ft.FilePicker()

    async def pick_image(e):
        files = await file_picker.pick_files(
            dialog_title='Виберіть зображення',
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['jpg', 'jpeg', 'png'],
            with_data=True,
        )
        if files:
            selected_file = files[0]
            selected_image['path'] = selected_file.path
            selected_image['name'] = selected_file.name
            selected_image['bytes'] = selected_file.bytes
            image_label.value = f'Вибрано: {selected_file.name}'
            image_label.color = ft.Colors.GREEN
        else:
            selected_image['path'] = None
            selected_image['name'] = None
            selected_image['bytes'] = None
            image_label.value = 'Зображення не вибрано'
            image_label.color = ft.Colors.RED
        page.update()

    def reload_products():
        products_list.controls.clear()
        products = load_json(ITEMS_PATH)

        if not products:
            products_list.controls.append(ft.Text('Товарів немає.', size=16))
            return

        for index, product in enumerate(products):
            async def delete_product(e, product_index=index):
                items = load_json(ITEMS_PATH)
                if 0 <= product_index < len(items):
                    items.pop(product_index)
                    save_json(items, ITEMS_PATH)
                reload_products()
                page.update()

            products_list.controls.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor='#F0F0F0',
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Image(src=product.get('image_src', ''), width=56, height=56, fit=ft.BoxFit.CONTAIN),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(product.get('name', ''), weight=ft.FontWeight.BOLD, size=15),
                                            ft.Text(
                                                f"Ціна: {format_price(product.get('price', 0))} | "
                                                f"В наявності: {product.get('qty', 0)} | "
                                                f"Виробник: {product.get('manufacturer', 'Невідомо')}"
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip='Видалити товар',
                                on_click=delete_product,
                            ),
                        ],
                    ),
                )
            )

    def reload_orders():
        orders_list.controls.clear()
        orders = load_orders()

        if not orders:
            orders_list.controls.append(ft.Text('Замовлень поки немає.', size=16))
            return

        for order in reversed(orders):
            status_dropdown = ft.Dropdown(
                value=order.get('status', 'created'),
                width=180,
                options=[ft.dropdown.Option(status, status_title(status)) for status in ORDER_STATUSES],
            )

            async def change_status(e, order_id=order.get('id'), dropdown=status_dropdown):
                if update_order_status(order_id, dropdown.value):
                    status_message.value = f'Статус замовлення #{order_id} змінено на "{status_title(dropdown.value)}".'
                    status_message.color = ft.Colors.GREEN
                else:
                    status_message.value = f'Не вдалося змінити статус замовлення #{order_id}.'
                    status_message.color = ft.Colors.RED
                status_message.visible = True
                reload_orders()
                page.update()

            status_dropdown.on_select = change_status

            orders_list.controls.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor='#F8F8F8',
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(f"Замовлення #{order.get('id')} · {order.get('created_at', '')}", weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"Користувач id {order.get('user', {}).get('id')}: "
                                        f"{order.get('user', {}).get('name', '')} {order.get('user', {}).get('surname', '')}"
                                    ),
                                    ft.Text(f"Сума: {format_price(order.get('total', 0))}"),
                                ],
                            ),
                            status_dropdown,
                        ],
                    ),
                )
            )

    reload_products()
    reload_orders()

    async def add_product(e):
        name = (name_input.value or '').strip()
        manufacturer = (manufacturer_input.value or '').strip() or 'PashaCustomCorporation'
        price = (price_input.value or '').strip()
        qty = (qty_input.value or '').strip()

        if not name or not price or not qty:
            message.value = 'Заповніть назву, ціну та кількість.'
            message.color = ft.Colors.RED
            message.visible = True
            page.update()
            return

        try:
            price_value = float(price)
            qty_value = int(qty)
        except ValueError:
            message.value = 'Ціна має бути числом, а кількість - цілим числом.'
            message.color = ft.Colors.RED
            message.visible = True
            page.update()
            return

        if price_value <= 0 or qty_value < 0:
            message.value = 'Ціна має бути більшою за 0, кількість не може бути відʼємною.'
            message.color = ft.Colors.RED
            message.visible = True
            page.update()
            return

        if selected_image['name']:
            filename = os.path.basename(selected_image['name'])
            assets_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
            os.makedirs(assets_dir, exist_ok=True)
            dst_path = os.path.join(assets_dir, filename)

            try:
                if selected_image['bytes']:
                    with open(dst_path, 'wb') as image_file:
                        image_file.write(selected_image['bytes'])
                elif selected_image['path']:
                    shutil.copy(selected_image['path'], dst_path)
                else:
                    raise OSError('Flet не повернув ані шлях, ані вміст файлу.')
            except OSError as err:
                message.value = f'Помилка копіювання файлу: {err}'
                message.color = ft.Colors.RED
                message.visible = True
                page.update()
                return
        else:
            filename = 'starkiller.jpg'

        new_product = {
            'name': name,
            'manufacturer': manufacturer,
            'price': str(price_value).rstrip('0').rstrip('.'),
            'qty': qty_value,
            'image_src': filename,
        }

        items = load_json(ITEMS_PATH)
        items.append(new_product)
        save_json(items, ITEMS_PATH)

        name_input.value = ''
        price_input.value = ''
        qty_input.value = ''
        selected_image['path'] = None
        selected_image['name'] = None
        selected_image['bytes'] = None
        image_label.value = 'Зображення не вибрано'
        image_label.color = ft.Colors.RED

        message.value = 'Товар успішно додано.'
        message.color = ft.Colors.GREEN
        message.visible = True

        reload_products()
        page.update()

    products = load_json(ITEMS_PATH)
    orders = load_orders()
    users = load_users()
    total_stock = sum(int(product.get('qty', 0)) for product in products)
    total_income = sum(float(order.get('total', 0)) for order in orders)

    add_form = ft.Container(
        padding=20,
        border_radius=8,
        bgcolor='#FAFAFA',
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Text('Додати новий товар', size=20, weight=ft.FontWeight.BOLD),
                name_input,
                manufacturer_input,
                ft.Row(controls=[price_input, qty_input], spacing=12),
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.FilledButton('Вибрати зображення', icon=ft.Icons.IMAGE, on_click=pick_image),
                        image_label,
                    ],
                ),
                message,
                ft.FilledButton(
                    'Додати товар',
                    icon=ft.Icons.ADD,
                    style=ft.ButtonStyle(bgcolor=DARK, color=ft.Colors.WHITE),
                    on_click=add_product,
                ),
            ],
        ),
    )

    return ft.View(
        route='/admin',
        scroll=ft.ScrollMode.AUTO,
        padding=0,

        appbar=main_appbar(page, '/admin'),
        controls=[
            ft.Container(
                gradient=BG_GRADIENT,
                    padding=24,
                    content=ft.Column(
                        spacing=24,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    info_chip(ft.Icons.GROUP, f'Користувачів: {len(users)}'),
                                    info_chip(ft.Icons.INVENTORY_2, f'Товарів: {len(products)}'),
                                    info_chip(ft.Icons.WAREHOUSE, f'Одиниць на складі: {total_stock}'),
                                    info_chip(ft.Icons.PAID, f'Продажі: {format_price(total_income)}'),
                                ],
                            ),
                            add_form,
                            ft.Divider(),
                            ft.Text('Список товарів', size=20, weight=ft.FontWeight.BOLD),
                            products_list,
                            ft.Divider(),
                            ft.Text('Замовлення', size=20, weight=ft.FontWeight.BOLD),
                            status_message,
                            orders_list,
                        ],
                    ),
                ),
            footer_bar(),
        ],
    )