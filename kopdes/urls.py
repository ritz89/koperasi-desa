from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from commerce.views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('item-detail/<item_id>/cart-add-item', add_order_item, name='add_order_item'),
    path('dashboard/', test2, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
