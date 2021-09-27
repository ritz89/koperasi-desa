from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from django.views import View

from commerce.models import Banner, ItemCategory, Item


def test(request):
    return render(request, 'commerce/pages/home-page/index.html')


def test2(request):
    return render(request, 'layouts/base-dashboard.html')


class HomePageView(View):

    def get(self, request):
        news = Banner.objects.all()
        kategori = ItemCategory.objects.all()
        item_queryset = Item.objects.all()
        if 'kategori' in request.GET:
            item_queryset = item_queryset.filter(category__category_name__icontains=request.GET['kategori'])
        if 'nama' in request.GET:
            item_queryset = item_queryset.filter(title__icontains=request.GET['nama'])
        p = Paginator(item_queryset, 6)
        if 'page' in request.GET:
            items = p.get_page(request.GET['page'])
        else:
            items = p.get_page(1)

        context = {
            'banner': news,
            'kategori': kategori,
            'items': items.object_list,
            'page_obj': items
        }
        if request.htmx:
            return render(request, 'commerce/pages/home-page/partials/item_lists.html', context)
        return render(request, 'commerce/pages/home-page/index.html', context)
