import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from commerce.forms import ItemForm, MediaLibraryForm
from commerce.models import Order, Item, ItemCategory, MediaLibrary


# Create your views here.


@login_required()
def manage_orders(request):
    if request.method == 'POST':
        if 'order_id' in request.POST and 'status' in request.POST:
            order_id = request.POST.get('order_id')
            status = request.POST.get('status')
            order = Order.objects.get(pk=order_id)
            if order.delivery.status == 3 or 5 or 6:
                return filter_order_mgm(request)
            order.delivery.status = status
            order.delivery.save()
            if status == 3 or 5 or 6:
                order.finish_date = datetime.datetime.now()
                order.save()

                for item in order.order_items.all():
                    if status == 3 or 5:
                        item.item.hold_stock -= item.qty
                        if item.item.hold_stock < 0:
                            item.item.hold_stock = 0
                            item.item.save()
                    else:
                        item.item.hold_stock -= item.qty
                        item.item.stock += item.qty
                        if item.item.hold_stock < 0:
                            item.item.hold_stock = 0
                            item.item.save()

    return filter_order_mgm(request)


def filter_order_mgm(request):
    status_filter = ''
    if 'status' in request.GET:
        status_filter = request.GET.get('status')
        orders = Order.objects.all().filter(delivery__status=status_filter, ordered=True)
    else:
        orders = Order.objects.all().filter(ordered=True)
    orders.order_by('id')
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'transparent_navbar': False,
        'page_obj': page_obj,
        'status_filter': status_filter
    }
    return render(request, 'commerce/pages/order-management/index.html', context)


@login_required
def inventory_management(request):
    items = Item.objects.all().order_by('id')
    item_category = ItemCategory.objects.all()

    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'item_category': item_category
    }
    return render(request, 'commerce/pages/item-management/index.html', context)


def edit_item_inventory(request, pk):
    item = Item.objects.get(pk=pk)
    form = ItemForm(instance=item)
    MediaFormSet = modelformset_factory(MediaLibrary, MediaLibraryForm, extra=3, can_delete=True, can_delete_extra=True)

    if request.method == 'POST':
        form = ItemForm(data=request.POST or None, files=request.FILES or None)
        formset = MediaFormSet(request.POST or None, files=request.FILES or None,
                               queryset=MediaLibrary.objects.none())
        if form.is_valid() and formset.is_valid():
            item_data = form.instance
            if not item_data.thumbnail:
                item_data.thumbnail = item.thumbnail
            item_data.id = item.id
            for cat in request.POST.getlist('category'):
                item_data.category.add(cat)
            item_data.save()
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    if image:
                        media = MediaLibrary(item=item_data, image=image)
                        media.save()
            context = {
                'form': form,
                'item': item,
                'formset': formset,
                'mode': 'Rubah',
                'transparent_navbar': False
            }
            return redirect('item-page', item.id)
        else:
            return HttpResponseRedirect("/")
    else:
        context = {
            'form': form,
            'item': item,
            'formset': MediaFormSet(queryset=MediaLibrary.objects.filter(item=item).all()),
            'mode': 'Rubah',
            'transparent_navbar': False
        }
        return render(request, 'commerce/pages/item-management/add_edit_item.html', context)


def tambah_item_inventory(request):

    form = ItemForm()
    MediaFormSet = modelformset_factory(MediaLibrary, MediaLibraryForm, extra=3, can_delete=True, can_delete_extra=True)

    if request.method == 'POST':
        form = ItemForm(data=request.POST or None, files=request.FILES or None)
        formset = MediaFormSet(request.POST or None, files=request.FILES or None,
                               queryset=MediaLibrary.objects.none())
        if form.is_valid() and formset.is_valid():
            item_data = form.instance
            item_data.save()
            for cat in request.POST.getlist('category'):
                item_data.category.add(cat)
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    if image:
                        media = MediaLibrary(item=item_data, image=image)
                        media.save()
            return redirect('item-page', item_data.id)
        else:
            return HttpResponseRedirect("/")
    else:
        context = {
            'form': form,
            'item': Item(),
            'formset': MediaFormSet(queryset=MediaLibrary.objects.none()),
            'mode': 'Tambah',
            'transparent_navbar': False
        }
        return render(request, 'commerce/pages/item-management/add_edit_item.html', context)

