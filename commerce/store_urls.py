from django.urls import path

from commerce.store_views import manage_orders, inventory_management, edit_item_inventory, tambah_item_inventory

urlpatterns = [
    path('manage-orders/', manage_orders, name='manage_orders'),
    path('inventories/', inventory_management, name='inventory_management'),
    path('edit-item/<pk>/', edit_item_inventory, name='edit_item_inventory'),
    path('tambah-item/', tambah_item_inventory, name='tambah-item_inventory'),
]
