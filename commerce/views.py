from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import DetailView

from commerce.forms import DeliveryForm
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
    if created:
        delivery = Delivery.objects.create(self_pick=True)
        user_order.delivery = delivery
        user_order.save()
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return HttpResponse(status=404)
    try:
        item_in_cart = user_order.order_items.get(item=item)
    except OrderItem.DoesNotExist:
        item_in_cart = OrderItem.objects.create(order=user_order, item=item, qty=0)
    if int(request.POST.get('qty')) > 0:
        item_in_cart.qty = request.POST.get('qty')
        item_in_cart.save()
    else:
        item_in_cart.delete()
    context = {
        'order': user_order,
    }
    print(user_order.total)
    if request.htmx:
        return render(request, 'layouts/partials/carts.html', context)
    return render(request, 'commerce/pages/shopping_cart/index.html', context)


class ShoppingCartView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        order = Order.objects.filter(user=request.user, ordered=False). \
            prefetch_related('order_items').prefetch_related('delivery').first()
        print(order)
        delivery_form = DeliveryForm()
        context = {
            'order': order,
            'delivery_form': delivery_form
        }
        return render(request, 'commerce/pages/shopping_cart/index.html', context)

    def post(self, request):
        try:
            order = Order.objects.select_related('delivery').get(pk=request.POST.get('id')). \
                prefetch_related('order_items')
        except Order.DoesNotExist:
            return HttpResponse(status=404)
        order.ordered = True
        context = {
            'order': order
        }
        return render(request, 'commerce/pages/shopping_cart/index.html', context)


@login_required()
def add_shopping_cart_item(request, pk):
    order_item = OrderItem.objects.get(pk=pk)
    if 'qty' in request.POST:
        quantity = int(request.POST.get('qty'))
    else:
        return
    if quantity > 0:
        order_item.qty = quantity
        order_item.save()
    else:
        order_item.delete()
    order = order_item.order
    context = {
        'order': order
    }
    return render(request, 'commerce/pages/shopping_cart/partials/order_items_list.html', context)


class ItemPage(DetailView):
    models = Item
    template_name = 'commerce/pages/item-details/index.html'
    context_object_name = 'item'
    queryset = Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            qs = OrderItem.objects.all().filter(order__user=self.request.user, item=context['item'],
                                                order__ordered=False).first()
            if qs:
                context['ordered'] = qs.qty
            else:
                context['ordered'] = 0
        else:
            context['ordered'] = 0
        context['items'] = Item.objects.all().filter(category__in=context['item'].category.all())
        return context


def delivery_options(request):
    if request.htmx:
        if request.GET['radioPengiriman'] == 'self_pick':
            return render(request, 'commerce/pages/shopping_cart/partials/self-pick-do.html')
        elif request.GET['radioPengiriman'] == 'dusun':
            return render(request, 'commerce/pages/shopping_cart/partials/dusun-do.html')
        else:
            return render(request, 'commerce/pages/shopping_cart/partials/location-do.html')
    return HttpResponse('<h1>Page was found</h1>')
