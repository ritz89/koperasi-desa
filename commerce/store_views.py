import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from commerce.models import Order


# Create your views here.


@login_required()
def manage_orders(request):
    if request.method == 'POST':
        if 'order_id' in request.POST and 'status' in request.POST:
            order_id = request.POST.get('order_id')
            status = request.POST.get('status')
            order = Order.objects.get(pk=order_id)
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

    orders = Order.objects.all().filter(ordered=True).order_by('id')

    if 'status' in request.GET:
        orders.filter(status=request.GET.get['status'])
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'transparent_navbar': False,
        'page_obj': page_obj
    }
    return render(request, 'commerce/pages/order-management/index.html', context)
