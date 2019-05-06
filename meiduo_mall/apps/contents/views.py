from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.category import get_categories


class IndexView(View):
    def get(self, request):
        categories = get_categories()
        context = {
            'categories': categories
        }
        return render(request, 'index.html', context)
