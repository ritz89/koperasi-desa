from django.shortcuts import render

# Create your views here.
from django.views import View


def test(request):
    return render(request, 'commerce/pages/home-page/index.html')


def test2(request):
    return render(request, 'layouts/base-dashboard.html')


class HomePageView(View):

    def get(self, request):
        return render(request, 'commerce/pages/home-page/index.html')
