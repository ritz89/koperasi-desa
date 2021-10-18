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


@login_required()
def manage_orders(request):
    orders = Order.objects.all().filter(ordered=True)
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
