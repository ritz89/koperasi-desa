import banner as banner
from django.shortcuts import render

# Create your views here.
from django.views import View

from commerce.models import Banner, ItemCategory


def test(request):
    return render(request, 'commerce/pages/home-page/index.html')


def test2(request):
    return render(request, 'layouts/base-dashboard.html')


class HomePageView(View):

    def get(self, request):
        news = Banner.objects.all()
        kategori = ItemCategory.objects.all()
        context = {
            'banner': news,
            'kategori': kategori,
        }
        return render(request, 'commerce/pages/home-page/index.html', context)
