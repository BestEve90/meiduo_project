from django.shortcuts import render

from django.views import View


class AdressesView(View):
    def get(self,request):
        return render(request,'user_center_site.html')

class AreaView(View):
    def get(self,request):
        area_id=request.GET.get('area_id')
        if not area_id:
            pass