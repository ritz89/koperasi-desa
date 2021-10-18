from commerce.models import OrderItem


def user_cart_ctx(request):
    if request.user.is_authenticated:
        data = OrderItem.objects.filter(order__user=request.user, order__ordered=False)
        return {
            'carts': data.all(),
            'carts_count': data.count(),
        }
    return {
        'carts': None,
        'carts_count': 0,
    }


def transparent_navbar_ctx(request):
    return {
        'transparent_navbar': True
    }
