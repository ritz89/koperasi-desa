from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from commerce.models import *


class ItemAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = [f.name for f in Item._meta.fields]
    list_filter = ['title', ]
    search_fields = [f.name for f in Item._meta.fields]


class OrderItemInlineAdmin(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInlineAdmin]


admin.site.register(Item, ItemAdmin)
admin.site.register(Address)
admin.site.register(Order, OrderAdmin)
admin.site.register(ItemCategory)
admin.site.register(MediaLibrary)
admin.site.register(Banner)

admin.site.register(Purchase)
admin.site.register(PurchaseItems)
admin.site.register(PosSales)
admin.site.register(PosSalesItems)
