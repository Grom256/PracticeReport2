from .home import home_view


def available_views():
    views = {}
    try:
        from .shop import shop_view
        views["/shop"] = shop_view
    except ImportError:
        pass
    try:
        from .product import product_view
        views["/product"] = product_view
    except ImportError:
        pass
    try:
        from .cart import cart_view
        views["/cart"] = cart_view
    except ImportError:
        pass
    try:
        from .login import login_view
        views["/login"] = login_view
    except ImportError:
        pass
    try:
        from .regist import regist_view
        views["/registration"] = regist_view
    except ImportError:
        pass
    try:
        from .settings import settings_view
        views["/settings"] = settings_view
    except ImportError:
        pass
    try:
        from .orders import orders_view
        views["/orders"] = orders_view
    except ImportError:
        pass
    try:
        from .admin import admin_view
        views["/admin"] = admin_view
    except ImportError:
        pass
    return views
