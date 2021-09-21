from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from commerce.views import test, test2

urlpatterns = [
    path('', test, name='test'),
    path('dashboard/', test2, name='dashboard'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
