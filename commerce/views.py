from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from commerce.models import Banner, ItemCategory, Item, MediaLibrary, Order, OrderItem, Delivery


def test(request):
    return render(request, 'commerce/pages/home-page/index.html')


def test2(request):
    return render(request, 'layouts/base-dashboard.html')


class HomePageView(View):

    def get(self, request):
        news = Banner.objects.all()
        kategori = ItemCategory.objects.all()
        item_queryset = Item.objects.all()
        if 'kategori' in request.GET:
            item_queryset = item_queryset.filter(category__category_name__icontains=request.GET['kategori'])
        if 'nama' in request.GET:
            item_queryset = item_queryset.filter(title__icontains=request.GET['nama'])
        p = Paginator(item_queryset, 6)
        if 'page' in request.GET:
            items = p.get_page(request.GET['page'])
        else:
            items = p.get_page(1)

        context = {
            'banner': news,
            'kategori': kategori,
            'items': items.object_list,
            'page_obj': items
        }
        if request.htmx:
            return render(request, 'commerce/pages/home-page/partials/item_lists.html', context)
        return render(request, 'commerce/pages/home-page/index.html', context)


@login_required
def add_order_item(request, item_id):
    user_order, created = Order.objects.get_or_create(user=request.user, ordered=False)
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return HttpResponse(status=404)
    try:
        item_in_cart = user_order.order_items.get(item=item)
    except OrderItem.DoesNotExist:
        item_in_cart = OrderItem.objects.create(order=user_order, item=item, qty=0)
    try:
        delivery = user_order.delivery
    except Delivery.DoesNotExist:
        delivery = Delivery.objects.create(order=user_order, address='',
                                           latitude=Delivery.koperasi_location['latitude'],
                                           longitude=Delivery.koperasi_location['longitude'], distance=0, status=1,
                                           delivery_cost=0)
    if int(request.POST.get('qty')) > 0:
        item_in_cart.qty = request.POST.get('qty')
        item_in_cart.save()
    else:
        item_in_cart.delete()
    context = {
        'order': user_order
    }
    print(user_order.total)
    if request.htmx:
        return render(request, 'layouts/partials/carts.html', context)
    return render(request, 'order/shopping-cart.html', context)

