from django import http
from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from .models import Areas

class AdressesView(View):
    def get(self,request):
        return render(request,'user_center_site.html')

class AreaView(View):
    def get(self,request):
        area_id=request.GET.get('area_id')
        province_list=[]
        if not area_id:
            provinces=Areas.objects.filter(parent__isnull=True)
            for province in provinces:
                province_list.append({'id':province.id,
                                      'name': province.name})
            return http.JsonResponse({'code':RETCODE.OK,'province_list':province_list})
        districts=Areas.objects.get(id=area_id)
        subs_list=[]
        sub_districts=districts.subs.all()
        for sub_district in sub_districts:
            subs_list.append({
                'id':sub_district.id,
                'name': sub_district.name
            })
        sub_data={
            'subs':subs_list
        }
        return http.JsonResponse({'code': RETCODE.OK, 'sub_data': sub_data})
