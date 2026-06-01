import flet as ft

from models import ITEMS_PATH, load_json
from views.components import DARK, GOLD, footer_bar, info_chip, main_appbar, BG_GRADIENT


def format_price(price):
    try:
        number = float(str(price).replace('$', '').strip())
        return f'${number:.2f}'.replace('.00', '')
    except (TypeError, ValueError):
        return f'${price}'


def product_price(product):
    try:
        return float(str(product.get('price', 0)).replace('$', '').strip() or 0)
    except ValueError:
        return 0


def create_product_card(page, product, product_index, message):
    async def open_product(e):
        await page.push_route(f'/product/{product_index}')

    async def quick_add(e):
        from views.cart import add_product_to_cart

        success, text = add_product_to_cart(page, product_index)
        message.value = text
        message.color = ft.Colors.GREEN if success else ft.Colors.RED
        message.visible = True
        page.update()

    qty = int(product.get('qty', 0))
    stock_text = 'Немає в наявності' if qty <= 0 else f'В наявності: {qty}'
    stock_color = ft.Colors.RED if qty <= 0 else ft.Colors.WHITE70

    return ft.Container(
        bgcolor='#1E1E24',
        border_radius=8,
        padding=12,
        shadow=ft.BoxShadow(
            blur_radius=12,
            color='#00000055',
            offset=ft.Offset(0, 4),
        ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    height=160,
                    bgcolor='#151518',
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Image(
                        src=product.get('image_src', ''),
                        fit=ft.BoxFit.CONTAIN,
                        border_radius=8,
                    ),
                ),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Text(
                            product.get('name', 'Товар без назви'),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            format_price(product.get('price', 0)),
                            size=15,
                            color=GOLD,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(stock_text, size=12, color=stock_color),
                    ],
                ),
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            'Переглянути',
                            icon=ft.Icons.VISIBILITY,
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLACK,
                                bgcolor=GOLD,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            expand=3,
                            on_click=open_product,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD_SHOPPING_CART,
                            tooltip='Додати в кошик',
                            disabled=qty <= 0,
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLACK,
                                bgcolor=GOLD,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            expand=1,
                            on_click=quick_add,
                        ),
                    ]
                ),
            ],
        ),
    )


def shop_view(page):
    async def go_to_settings(e):
        await page.push_route('/settings')

    async def go_home(e):
        await page.push_route('/')

    async def go_to_cart(e):
        await page.push_route('/cart')

    async def go_to_orders(e):
        await page.push_route('/orders')

    products = load_json(ITEMS_PATH)
    message = ft.Text(visible=False)
    cards_grid = ft.GridView(
        expand=True,
        max_extent=300,
        child_aspect_ratio=0.72,
        spacing=20,
        run_spacing=20,
    )
    empty_state = ft.Container(
        padding=32,
        alignment=ft.Alignment.CENTER,
        visible=False,
        content=ft.Text('За вибраними фільтрами товарів не знайдено.', size=18),
    )

    search_input = ft.TextField(
        label='Пошук',
        value=getattr(page, 'shop_query', ''),
        prefix_icon=ft.Icons.SEARCH,
        width=320,
    )
    sort_dropdown = ft.Dropdown(
        label='Сортування',
        value=getattr(page, 'shop_sort', 'name'),
        width=220,
        options=[
            ft.dropdown.Option('name', 'За назвою'),
            ft.dropdown.Option('price_asc', 'Ціна: від меншої'),
            ft.dropdown.Option('price_desc', 'Ціна: від більшої'),
            ft.dropdown.Option('qty_desc', 'Наявність'),
        ],
    )
    stock_switch = ft.Switch(
        label='Лише в наявності',
        value=bool(getattr(page, 'shop_in_stock_only', False)),
        active_color=GOLD,
    )

    def filtered_products():
        query = (search_input.value or '').strip().lower()
        sort_mode = sort_dropdown.value or 'name'
        in_stock_only = bool(stock_switch.value)

        result = []
        for index, product in enumerate(products):
            text = f"{product.get('name', '')} {product.get('manufacturer', '')}".lower()
            if query and query not in text:
                continue
            if in_stock_only and int(product.get('qty', 0)) <= 0:
                continue
            result.append((index, product))

        if sort_mode == 'price_asc':
            result.sort(key=lambda pair: product_price(pair[1]))
        elif sort_mode == 'price_desc':
            result.sort(key=lambda pair: product_price(pair[1]), reverse=True)
        elif sort_mode == 'qty_desc':
            result.sort(key=lambda pair: int(pair[1].get('qty', 0)), reverse=True)
        else:
            result.sort(key=lambda pair: pair[1].get('name', ''))

        page.shop_query = search_input.value or ''
        page.shop_sort = sort_mode
        page.shop_in_stock_only = in_stock_only
        return result

    def render_products():
        cards_grid.controls.clear()
        items = filtered_products()
        for index, product in items:
            cards_grid.controls.append(create_product_card(page, product, index, message))
        cards_grid.visible = bool(items)
        empty_state.visible = not bool(items)

    async def apply_filters(e):
        render_products()
        page.update()

    search_input.on_submit = apply_filters
    sort_dropdown.on_select = apply_filters
    stock_switch.on_change = apply_filters
    render_products()

    total_items = len(products)
    available_items = sum(1 for product in products if int(product.get('qty', 0)) > 0)

    return ft.View(
        route='/shop',
        padding=0,
        spacing=0,
        appbar=main_appbar(page, '/shop'),
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
                gradient=ft.SweepGradient(
                    center=ft.Alignment.CENTER,
                    colors=[
                        ft.Colors.GREY_900,  # темний метал
                        ft.Colors.GREY_300,  # світлий метал (блік)
                        ft.Colors.AMBER,
                        ft.Colors.GREY_200,  # ще один блік
                        ft.Colors.YELLOW,
                        ft.Colors.GREY_900,
                    ],
                    rotation=0.35,
                ),
                    padding=24,
                    content=ft.Column(
                        spacing=18,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            info_chip(ft.Icons.INVENTORY_2, f'Товарів: {total_items}'),
                                            info_chip(ft.Icons.CHECK_CIRCLE, f'Доступно: {available_items}'),
                                        ],
                                    ),
                                    message,
                                ],
                            ),
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    search_input,
                                    sort_dropdown,
                                    stock_switch,
                                    ft.FilledButton(
                                        'Застосувати',
                                        icon=ft.Icons.FILTER_ALT,
                                        style=ft.ButtonStyle(bgcolor=DARK, color=ft.Colors.WHITE),
                                        on_click=apply_filters,
                                    ),
                                ],
                            ),
                            cards_grid,
                            # empty_state,
                        ],
                    ),
                ),
            footer_bar(),
        ],
    )