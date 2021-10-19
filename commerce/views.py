import datetime
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView

from commerce.forms import DeliveryForm, AddressFormDusun, ProfileForm
from commerce.models import Banner, ItemCategory, Item, MediaLibrary, Order, OrderItem, Delivery, Address, UserProfile


def test(request):
    return render(request, 'commerce/pages/home-page/index.html')


def test2(request):
    return render(request, 'commerce/pages/shopping_history/index.html', {'transparent_navbar': False})


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
        item_in_cart = OrderItem.objects.create(order=user_order, item=item, qty=0, price=item.price)

    quantity = int(request.POST.get('qty'))
    update_qty = quantity - item_in_cart.qty
    err_msg = ''
    if quantity < 0:
        err_msg = 'pemesanan tidak bisa kurang dari nol'
        context = {
            'order': user_order,
            'err_msg': err_msg,
            'item': item,
            'ordered': user_order.order_items.get(item=item).qty
        }
        if request.htmx:
            return render(request, 'layouts/partials/carts.html', context)
        return render(request, 'commerce/pages/item-details/index.html', context)
    if item_in_cart.item.stock < update_qty:
        err_msg = 'pemesanan melebihi stok yang ada'
        context = {
            'order': user_order,
            'err_msg': err_msg,
            'item': item,
            'ordered': user_order.order_items.get(item=item).qty
        }
        if request.htmx:
            return render(request, 'layouts/partials/carts.html', context)
        return render(request, 'commerce/pages/item-details/index.html', context)
    if quantity > 0:
        item_in_cart.qty = quantity
        item_in_cart.item.hold_stock += update_qty
        item_in_cart.item.stock -= update_qty
        item_in_cart.item.save()
        item_in_cart.save()
    else:
        if item_in_cart.qty > 0:
            item_in_cart.item.qty += item_in_cart.qty
            item_in_cart.item.hold_stock -= item_in_cart.qty
            item_in_cart.item.save()
        item_in_cart.delete()

    context = {
        'order': user_order,
        'err_msg': err_msg,
        'item': item,
        'ordered': user_order.order_items.get(item=item).qty
    }
    if request.htmx:
        return render(request, 'layouts/partials/carts.html', context)
    return render(request, 'commerce/pages/item-details/index.html', context)


class ShoppingCartView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        order = Order.objects.filter(user=request.user, ordered=False). \
            prefetch_related('order_items').prefetch_related('delivery').first()
        if order is None:
            order = Order.objects.create(user=request.user, ordered=False,
                                         delivery=Delivery.objects.create(self_pick=True))
        address = Address.objects.filter(user=request.user)
        address_form = AddressFormDusun()
        context = {
            'order': order,
            'address': address,
            'form': address_form,
            'err_msg':''
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
def konfirmasi_order_ambil_sendiri(request, pk=None):
    try:
        order = Order.objects.get(pk=pk)
        if order.total <= 0:
            return redirect('home')
        order.delivery.self_pick = True
        order.delivery.status = 4
        order.delivery.save()
        order.ordered_date = datetime.date.today()
        order.ordered = True
        order.save()
    except Order.DoesNotExist:
        return HttpResponse(status=404)
    return redirect('history-belanja')


@login_required()
def konfirmasi_order(request, pk=None):
    try:
        order = Order.objects.get(pk=pk)
        if order.total <= 0:
            return redirect('home')
        order.ordered_date = datetime.date.today()
        order.ordered = True
        order.save()
    except Order.DoesNotExist:
        return HttpResponse(status=404)
    return redirect('history-belanja')


@login_required()
def address_form_dusun(request):
    form = AddressFormDusun()
    return render(request, 'commerce/pages/shopping_cart/partials/alamat-edit.html', {'form': form})


@login_required()
def address_detail(request, pk):
    address = Address.objects.get(pk=pk)
    return render(request, 'commerce/pages/shopping_cart/partials/alamat-show.html', {'address': address})


@login_required()
def add_shopping_cart_item(request, pk):
    order_item = OrderItem.objects.get(pk=pk)
    if 'qty' in request.POST:
        quantity = int(request.POST.get('qty'))
    else:
        return
    update_qty = quantity - order_item.qty
    err_msg = 'aaa'
    if quantity < 0:
        err_msg = 'pemesanan tidak bisa kurang dari nol'
        order = Order.objects.get(pk=order_item.order.id)
        context = {
            'order': order,
            'err_msg': err_msg
        }
        return render(request, 'commerce/pages/shopping_cart/partials/order_items_list.html', context)
    if order_item.item.stock < update_qty:
        err_msg = 'pemesanan melebihi stok yang ada'
        order = Order.objects.get(pk=order_item.order.id)
        context = {
            'order': order,
            'err_msg': err_msg
        }
        return render(request, 'commerce/pages/shopping_cart/partials/order_items_list.html', context)
    if quantity > 0:
        order_item.qty = quantity
        order_item.item.hold_stock += update_qty
        order_item.item.stock -= update_qty
        order_item.item.save()
        order_item.save()
    else:
        if order_item.qty > 0:
            order_item.item.stock += order_item.qty
            order_item.item.hold_stock -= order_item.qty
            order_item.item.save()
        order_item.delete()
    order = order_item.order
    context = {
        'order': order,
        'err_msg': err_msg
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


@login_required()
def simpan_alamat(request):
    form = AddressFormDusun(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.distance = address.get_distance()
            address.save()
            base_url = reverse('set-alamat')
            qs = urlencode({'address-selector': address.id})
            return redirect('{}?{}'.format(base_url, qs))
        else:
            return render(request, 'commerce/pages/shopping_cart/partials/alamat-edit.html',
                          context={'form': form}
                          )


@login_required()
def set_alamat(request):
    order = Order.objects.filter(user=request.user, ordered=False).first()
    pk = request.GET.get('address-selector')
    form = AddressFormDusun()
    if int(pk) > 0:
        address = Address.objects.get(pk=pk)
        order.delivery.address = address
        order.delivery.self_pick = False
        order.delivery.distance = address.distance
        order.delivery.status = 1
        order.delivery.save()
        order.save()
        return render(request, 'commerce/pages/shopping_cart/partials/sc-address-show.html',
                      {'order': order, 'form': form})
    order.delivery.self_pick = True
    order.delivery.save()
    order.save()
    return render(request, 'commerce/pages/shopping_cart/partials/selfpick-form.html', {'order': order, 'form': form})


@login_required()
def histori_belanja(request):
    order = Order.objects.filter(user=request.user, ordered=True).all()
    context = {
        'orders': order,
        'transparent_navbar': False
    }
    return render(request, 'commerce/pages/shopping_history/index.html', context)


@login_required()
def hapus_order(request, pk):
    order = Order.objects.get(pk=pk)

    if order.user != request.user:
        return redirect('home')

    if order.delivery.status == 2 or 3 or 5 or 6:
        return redirect('history-belanja')

    order.status = 6
    order.save()
    return redirect('history-belanja')


@login_required()
def profile(request):
    profile_form = ProfileForm(data=request.POST or None, files=request.FILES or None)
    try:
        current_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        current_profile = UserProfile.objects.create(user=request.user)
    riwayat_transaksi = Order.objects.filter(user=request.user)
    total_order = Order.objects.filter(user=request.user).count()
    selesai = Order.objects.filter(user=request.user).filter(Q(delivery__status=3) or Q(delivery__status=5)).count()
    if request.method == 'POST':
        if profile_form.is_valid():
            profil = profile_form.instance
            if not profil.profile_picture:
                profil.profile_picture = current_profile.profile_picture
            profil.id = current_profile.id
            profil.user = request.user
            profil.save()
            return redirect('get-profile-widget')
        else:
            return render(request, 'commerce/pages/user-profile/partials/profile-form.html',
                          {'profile_form': profile_form})
    context = {
        'profile_form': profile_form,
        'transparent_navbar': False,
        'riwayat_transaksi': riwayat_transaksi,
        'total_order': total_order,
        'selesai': selesai,
    }
    return render(request, 'commerce/pages/user-profile/index.html', context)


def get_profile_form(request):
    profil, created = UserProfile.objects.get_or_create(user=request.user)
    profile_form = ProfileForm(instance=profil)
    context = {
        'profile_form': profile_form,
        'transparent_navbar': False
    }
    return render(request, 'commerce/pages/user-profile/partials/profile-form.html', context)


def get_profile_widget(request):
    profil, created = UserProfile.objects.get_or_create(user=request.user)
    profile_form = ProfileForm(instance=profil)
    context = {
        'profile_form': profile_form,
        'transparent_navbar': False
    }
    return render(request, 'commerce/pages/user-profile/partials/profile-widget.html', context)
