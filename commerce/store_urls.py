from django.urls import path

from commerce.store_views import manage_orders

urlpatterns = [
    path('manage-orders', manage_orders, name='manage_orders'),
]
