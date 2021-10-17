import hijack
import hijack as hijack
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from commerce.views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('item-detail/<item_id>/cart-add-item', add_order_item, name='add_order_item'),
    path('shopping-cart/', ShoppingCartView.as_view(), name='shopping_cart'),
    path('shopping-cart/item/<pk>/', add_shopping_cart_item, name='shopping_cart_item_update'),
    path('item-details/<pk>/', ItemPage.as_view(), name='item-page'),
    path('dashboard/', test2, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('confirm-self-pickup-order/<pk>/', konfirmasi_order_ambil_sendiri, name='confirm-self-pick'),
    path('confirm-order/<pk>/', konfirmasi_order, name='confirm-order'),
    path('htmx/address-form/', address_form_dusun, name='address-form-dusun'),
    path('htmx/address-save/', simpan_alamat, name='simpan-alamat'),
    path('htmx/address-detail/<pk>', address_detail, name='address-detail'),
    path('htmx/show-address/', set_alamat, name='set-alamat')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
