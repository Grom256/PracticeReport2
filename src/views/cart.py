import flet as ft

from models import ITEMS_PATH, create_order, load_json, save_json, validate_payment
from views.components import GOLD, footer_bar, main_appbar
from views.shop import format_price

PANEL_BG = '#C7C7C7'
ITEM_BG = '#1a1a2e'


def get_cart(page):
    if not hasattr(page, 'cart'):
        page.cart = []
    return page.cart


def add_product_to_cart(page, product_index):
    products = load_json(ITEMS_PATH)
    if product_index < 0 or product_index >= len(products):
        return False, 'Товар не знайдено.'

    available_qty = int(products[product_index].get('qty', 0))
    cart = get_cart(page)

    for item in cart:
        if item['product_index'] == product_index:
            if item['qty'] >= available_qty:
                return False, 'Немає достатньої кількості товару.'
            item['qty'] += 1
            return True, 'Товар додано в кошик.'

    if available_qty <= 0:
        return False, 'Товару немає в наявності.'

    cart.append({'product_index': product_index, 'qty': 1})
    return True, 'Товар додано в кошик.'


def get_cart_products(page):
    products = load_json(ITEMS_PATH)
    result = []
    for cart_item in get_cart(page):
        i = cart_item.get('product_index')
        if i is None or i < 0 or i >= len(products):
            continue
        product = products[i]
        result.append({
            'product_index': i,
            'name': product.get('name', 'Товар без назви'),
            'manufacturer': product.get('manufacturer', 'Невідомо'),
            'price': product.get('price', 0),
            'qty': int(cart_item.get('qty', 1)),
            'image_src': product.get('image_src', ''),
        })
    return result


def get_cart_total(cart_products):
    total = 0
    for item in cart_products:
        try:
            price = float(str(item.get('price', 0)).replace('$', ''))
        except Exception:
            price = 0
        total += price * int(item.get('qty', 1))
    return round(total, 2)


def mask_card_number(card_number):
    digits = ''.join(ch for ch in card_number if ch.isdigit())
    return f'**** **** **** {digits[-4:]}' if len(digits) >= 4 else '****'




def cart_view(page):
    current_user = getattr(page, 'current_user', None)

    def close_dialog():
        page.pop_dialog()

    def open_dialog(dialog):
        if not dialog.open:
            page.show_dialog(dialog)


    cart_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text('', size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)

    def build_cart_rows():
        cart_products = get_cart_products(page)
        rows = []
        for item in cart_products:
            idx = item['product_index']

            async def on_remove(e, i=idx):
                for ci in list(get_cart(page)):
                    if ci['product_index'] == i:
                        get_cart(page).remove(ci)
                        break
                refresh_cart()

            async def on_increase(e, i=idx):
                products = load_json(ITEMS_PATH)
                available = int(products[i].get('qty', 0))
                for ci in get_cart(page):
                    if ci['product_index'] == i:
                        if ci['qty'] < available:
                            ci['qty'] += 1
                        break
                refresh_cart()

            async def on_decrease(e, i=idx):
                for ci in list(get_cart(page)):
                    if ci['product_index'] == i:
                        ci['qty'] -= 1
                        if ci['qty'] <= 0:
                            get_cart(page).remove(ci)
                        break
                refresh_cart()

            rows.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor=ITEM_BG,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Image(src=item['image_src'], width=64, height=64, fit=ft.BoxFit.CONTAIN),
                                    ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                item['name'],
                                                weight=ft.FontWeight.BOLD,
                                                max_lines=2,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Text(format_price(item['price']), color=GOLD),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.Icons.REMOVE, on_click=on_decrease, icon_color=ft.Colors.WHITE),
                                    ft.Text(
                                        str(item['qty']),
                                        width=24,
                                        text_align=ft.TextAlign.CENTER,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.IconButton(ft.Icons.ADD, on_click=on_increase, icon_color=ft.Colors.WHITE),
                                    ft.IconButton(ft.Icons.DELETE, on_click=on_remove, icon_color=ft.Colors.RED_300),
                                ],
                            ),
                        ],
                    ),
                )
            )
        return cart_products, rows

    def refresh_cart():
        cart_products, rows = build_cart_rows()
        cart_column.controls.clear()
        if rows:
            cart_column.controls.extend(rows)
        else:
            cart_column.controls.append(
                ft.Text('Кошик порожній.', size=18, color=ft.Colors.WHITE)
            )
        total_text.value = f'Разом: {format_price(get_cart_total(cart_products))}'
        page.update()

    refresh_cart()

    async def clear_cart(e):
        page.cart = []
        refresh_cart()


    payment_error = ft.Text('', color=ft.Colors.RED_700, visible=False, size=13)

    payment_method = ft.Dropdown(
        label='Спосіб оплати',
        value='card',
        options=[
            ft.dropdown.Option('card', 'Банківська картка'),
            ft.dropdown.Option('paypal', 'PayPal'),
        ],
        width=340,
    )
    card_holder = ft.TextField(label="Ім'я власника картки", width=340)
    card_number = ft.TextField(label='Номер картки', hint_text='4111111111111111', width=340)
    card_expiry = ft.TextField(label='Термін дії', hint_text='MM/YY', width=160)
    card_cvv = ft.TextField(label='CVV', password=True, width=160)
    card_details_row = ft.Row(controls=[card_expiry, card_cvv])
    paypal_email = ft.TextField(
        label='PayPal email',
        keyboard_type=ft.KeyboardType.EMAIL,
        width=340,
    )

    def set_payment_visibility():

        is_card = payment_method.value == 'card'
        card_holder.visible = is_card
        card_number.visible = is_card
        card_expiry.visible = is_card
        card_cvv.visible = is_card
        card_details_row.visible = is_card
        paypal_email.visible = not is_card
        payment_error.visible = False

    def on_payment_method_change(e):
        set_payment_visibility()
        payment_dialog.update()

    payment_method.on_select = on_payment_method_change
    set_payment_visibility()


    thank_you_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text('Дякуємо за замовлення! 🎉', size=20, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True,
            spacing=8,
            controls=[
                ft.Text('Ваше замовлення успішно оформлено.', size=15),
                ft.Text(
                    'Ми надішлемо підтвердження на вашу електронну пошту.',
                    size=13,
                    color=ft.Colors.BLACK54,
                ),
            ],
        ),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    async def close_thank_you(e):
        close_dialog()
        await page.push_route('/orders')

    thank_you_dialog.actions.append(
        ft.FilledButton('Мої замовлення', icon=ft.Icons.RECEIPT_LONG, on_click=close_thank_you)
    )


    payment_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text('Оплата замовлення', size=20, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True,
            spacing=10,
            width=360,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text('Оберіть спосіб оплати та введіть дані.', size=13, color=ft.Colors.BLACK54),
                payment_method,
                card_holder,
                card_number,
                card_details_row,
                paypal_email,
                payment_error,
            ],
        ),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    async def cancel_payment(e):
        close_dialog()

    async def confirm_payment(e):
        cart_products = get_cart_products(page)

        success, text = validate_payment(
            payment_method.value,
            card_number.value or '',
            card_expiry.value or '',
            card_cvv.value or '',
            card_holder.value or '',
            paypal_email.value or '',
        )
        if not success:
            payment_error.value = text
            payment_error.visible = True
            page.update()
            return

        products = load_json(ITEMS_PATH)
        for item in cart_products:
            idx = item['product_index']
            if int(products[idx].get('qty', 0)) < int(item['qty']):
                payment_error.value = f"Недостатньо товару: {item['name']}."
                payment_error.visible = True
                page.update()
                return

        payment_details = {}
        if payment_method.value == 'card':
            payment_details = {
                'card_holder': card_holder.value,
                'card_number': mask_card_number(card_number.value),
            }
        elif payment_method.value == 'paypal':
            payment_details = {'paypal_email': paypal_email.value}

        create_order(
            current_user,
            cart_products,
            payment_method.value,
            payment_details,
            delivery_address={
                'country': country_dropdown.value,
                'city': city_field.value.strip(),
                'address': address_field.value.strip(),
                'postal': postal_field.value.strip(),
            },
        )

        for item in cart_products:
            idx = item['product_index']
            products[idx]['qty'] = int(products[idx].get('qty', 0)) - int(item['qty'])
        save_json(products, ITEMS_PATH)

        page.cart = []
        close_dialog()
        refresh_cart()
        open_dialog(thank_you_dialog)

    payment_dialog.actions.extend([
        ft.OutlinedButton('Скасувати', on_click=cancel_payment),
        ft.FilledButton('Сплатити', icon=ft.Icons.PAYMENT, on_click=confirm_payment),
    ])

    # ── delivery panel ────────────────────────────────────────────────────────
    async def go_to_login(e):
        await page.push_route('/login')

    if current_user:
        recipient_name = f"{current_user.get('name', '')} {current_user.get('surname', '')}".strip()
        recipient_phone = current_user.get('phone', '')

        delivery_error = ft.Text('', color=ft.Colors.RED_700, visible=False, size=13)

        COUNTRIES = [
            'Україна',
            'США',
            'Китай',
            'Німеччина',
            'Японія',
            'Індія',
            'Велика Британія',
            'Франція',
            'Канада',
            'Італія',
            'Бразилія',
            'Австралія',
            'Південна Корея',
            'Нідерланди',
            'Іспанія',
            'Швейцарія',
            'Польща',
            'Швеція',
            'Бельгія',
            'Норвегія',
        ]

        country_dropdown = ft.Dropdown(
            label='Країна',
            value='Україна',
            width=340,
            options=[ft.dropdown.Option(c) for c in COUNTRIES],
        )
        city_field = ft.TextField(label='Місто', width=340)
        address_field = ft.TextField(label='Вулиця, будинок, квартира', width=340)
        postal_field = ft.TextField(label='Поштовий індекс', width=340)

        async def go_to_payment(e):
            if not country_dropdown.value:
                delivery_error.value = 'Оберіть країну доставки.'
                delivery_error.visible = True
                page.update()
                return
            if not city_field.value.strip():
                delivery_error.value = 'Введіть місто.'
                delivery_error.visible = True
                page.update()
                return
            if not address_field.value.strip():
                delivery_error.value = 'Введіть адресу доставки.'
                delivery_error.visible = True
                page.update()
                return
            if not postal_field.value.strip():
                delivery_error.value = 'Введіть поштовий індекс.'
                delivery_error.visible = True
                page.update()
                return
            if not get_cart_products(page):
                delivery_error.value = 'Кошик порожній.'
                delivery_error.visible = True
                page.update()
                return

            # Reset payment form before opening
            payment_method.value = 'card'
            card_holder.value = ''
            card_number.value = ''
            card_expiry.value = ''
            card_cvv.value = ''
            paypal_email.value = ''
            set_payment_visibility()
            delivery_error.visible = False
            open_dialog(payment_dialog)

        panel_content = ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Text('Доставка', size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                # Free shipping chip
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=8,
                    bgcolor='#E8F5E9',
                    content=ft.Row(
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_SHIPPING, color=ft.Colors.GREEN_700, size=18),
                            ft.Text(
                                'Доставка безкоштовна',
                                color=ft.Colors.GREEN_800,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                ),
                # Recipient block (read-only info)
                ft.Text('Отримувач', size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK54),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=8,
                    bgcolor='#EBEBEB',
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(recipient_name, color=ft.Colors.BLACK87, weight=ft.FontWeight.W_500),
                            ft.Text(recipient_phone, color=ft.Colors.BLACK54, size=13),
                        ],
                    ),
                ),
                # Address fields
                ft.Text('Адреса доставки', size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK54),
                country_dropdown,
                city_field,
                address_field,
                postal_field,
                delivery_error,
                ft.Divider(color=ft.Colors.BLACK26),
                total_text,
                ft.FilledButton(
                    'Перейти до оплати',
                    icon=ft.Icons.PAYMENT,
                    on_click=go_to_payment,
                    width=340,
                ),
                ft.OutlinedButton(
                    'Очистити кошик',
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=clear_cart,
                    width=340,
                ),
            ],
        )
    else:
        panel_content = ft.Column(
            spacing=14,

            controls=[
                total_text,
                ft.Text(
                    'Оформити замовлення можна тільки після входу в акаунт.',
                    color=ft.Colors.RED_700,
                ),
                ft.FilledButton('Увійти в акаунт', icon=ft.Icons.LOGIN, on_click=go_to_login),
                ft.OutlinedButton(
                    'Очистити кошик',
                    icon=ft.Icons.DELETE_OUTLINE,
                    on_click=clear_cart,
                ),
            ],
        )

    # ── assemble view ─────────────────────────────────────────────────────────
    return ft.View(
        route='/cart',
        padding = 0,
        appbar=main_appbar(page, '/cart'),
        bottom_appbar=footer_bar(),
        controls=[
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=['#000000', ft.Colors.GREY_300, '#FFE900'],
                ),
                padding=24,
                content=ft.Row(
                    spacing=28,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        # Left: cart items
                        ft.Container(
                            expand=True,
                            content=cart_column,
                        ),
                        # Right: delivery / checkout panel
                        ft.Container(
                            width=420,
                            padding=16,
                            border_radius=8,
                            bgcolor=PANEL_BG,
                            content=panel_content,
                        ),
                    ],
                ),
            ),
        ],
    )
