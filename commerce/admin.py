from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from commerce.models import Item, OrderItem, Order, ItemCategory, MediaLibrary, Banner


class ItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [f.name for f in Item._meta.fields]
    list_filter = ['title', ]
    search_fields = [f.name for f in Item._meta.fields]


admin.site.register(Item, ItemAdmin)

admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ItemCategory)
admin.site.register(MediaLibrary)
admin.site.register(Banner)
