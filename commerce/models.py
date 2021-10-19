import os
from enum import auto

import requests
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.
from django.conf import settings


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class UserProfile(models.Model):
    fullname = models.CharField(max_length=100, default='')
    no_hp = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='user/profile_pictures', storage=OverwriteStorage())
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_profile')


class ItemCategory(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


class MediaLibrary(models.Model):
    image = models.ImageField(upload_to='app_medias', storage=OverwriteStorage())
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class Item(models.Model):
    title = models.CharField(max_length=100)
    category = models.ManyToManyField(ItemCategory)
    description = models.TextField()
    price = models.IntegerField()
    stock = models.IntegerField()
    thumbnail = models.ImageField(upload_to='app_medias/thumbnails', null=True, storage=OverwriteStorage())
    hold_stock = models.IntegerField(default=0)
    media = models.ManyToManyField(MediaLibrary)

    deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def add_stock(self, qty):
        self.stock += qty
        self.save()

    def remove_stock(self, qty):
        self.stock -= qty
        self.save()

    def __str__(self):
        return self.title


class Dusun(models.Model):
    no = models.IntegerField()
    name = models.CharField(max_length=50)
    ongkir = models.IntegerField()

    def __str__(self):
        return self.name


class Address(models.Model):
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    dusun = models.ForeignKey(Dusun, null=True, on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    distance = models.IntegerField(default=0)

    def get_distance(self):
        if self.latitude and self.longitude:
            headers = {
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            }
            call = requests.get(
                'https://api.openrouteservice.org/v2/directions/driving-car?api_key'
                '=5b3ce3597851110001cf624860dd45501cb64305a4fb8c8d2b012616&start='
                '117.060181,-0.588735&end={longitude},{latitude}'.format(longitude=self.longitude,
                                                                         latitude=self.latitude),
                headers=headers)
            data = call.json()
            return int(data['features'][0]['properties']['summary']['distance']) / 1000
        else:
            return -1


class Delivery(models.Model):
    DELIVERY_STATUS = [
        (1, 'Dipersiapkan'),
        (2, 'Proses Pengantaran'),
        (3, 'Telah Diantarkan'),
        (4, 'Belum Diambil'),
        (5, 'Telah diambil'),
        (6, 'Dibatalkan')
    ]

    koperasi_location = {
        'latitude': '-0.588735',
        'longitude': '117.060181'
    }

    address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    status = models.IntegerField(choices=DELIVERY_STATUS, default=1)
    self_pick = models.BooleanField(default=True)
    distance = models.FloatField(default=0)

    def status_verbose(self):
        return dict(Delivery.DELIVERY_STATUS)[self.status]

    @property
    def delivery_cost(self):
        if self.self_pick:
            return 0
        elif self.address.dusun:
            return self.address.dusun.ongkir
        else:
            if self.address.distance < 0:
                return 99999999
            elif self.address.distance < 10:
                return 8000
            else:
                return int((8000 + (self.address.distance - 10) * 1500) / 1000) * 1000


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order')
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True)
    ordered = models.BooleanField(default=False)
    delivery = models.OneToOneField(Delivery, on_delete=models.CASCADE, related_name='order', null=True)
    finish_date = models.DateTimeField(null=True, blank=True)

    @property
    def subtotal(self):
        subtotal = 0
        for item in self.order_items.all():
            subtotal += item.price * item.qty
        return subtotal

    @property
    def total(self):
        try:
            return self.subtotal + self.delivery.delivery_cost
        except Delivery.DoesNotExist:
            return self.subtotal


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_item')
    qty = models.FloatField()
    price = models.IntegerField(default=0)

    @property
    def subtotal(self):
        return self.price * self.qty

    def __str__(self):
        return self.item.title


class SourceAddress(models.Model):
    address = models.TextField()
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)


class Purchase(models.Model):
    PURCHASE_STATUS = (
        ('u', 'unpaid'),
        ('p', 'paid'),
        ('c', 'cancelled')
    )
    description = models.TextField()
    purchase_date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=PURCHASE_STATUS)
    purchase_source = models.ForeignKey(SourceAddress, on_delete=models.CASCADE)


class PurchaseItems(models.Model):
    purchasing = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='purchase_item')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchase_item')
    qty = models.IntegerField(default=1)
    purchase_price = models.IntegerField()


class TransactionJournals(models.Model):
    periode_form = models.DateField()
    periode_to = models.DateField()
    posted = models.BooleanField(default=False)


class TransactionJournalsItems(models.Model):
    TRX_TYPE = (
        ('s', 'sales'),
        ('p', 'purchasing')
    )

    trx_ref = models.CharField(max_length=100)
    trx_type = models.CharField(choices=TRX_TYPE, max_length=1)
    item = models.ForeignKey(Item, related_name='transaction_journal_item', on_delete=models.CASCADE)
    qty = models.IntegerField()
    journal = models.ForeignKey(TransactionJournals, on_delete=models.CASCADE, related_name='journal_item')


class SupplyRequest(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='supply_request')
    qty = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class PosSales(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    dtm_sales = models.DateTimeField(auto_now_add=True)


class PosSalesItems(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, related_name='sales_items', null=True)
    sales_price = models.FloatField(default=0)
    qty = models.IntegerField(default=0)


class Banner(models.Model):
    title = models.CharField(max_length=50)
    messages = models.CharField(max_length=100)
    image = models.ImageField(null=True)
