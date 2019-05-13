from django.shortcuts import render
from django.views import View


class PlaceOrderView(View):
    def get(self, request):
        return render(request, 'place_order.html')
