from django import http
from django.core.cache import cache
from django.shortcuts import render
from django.views import View

from areas import constants
from meiduo_mall.utils.response_code import RETCODE
from .models import Areas


class AdressesView(View):
    def get(self, request):
        return render(request, 'user_center_site.html')


class AreaView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')

        if area_id is None:
            province_list = cache.get('province_list')
            if province_list is None:
                provinces = Areas.objects.filter(parent__isnull=True)
                province_list = []
                for province in provinces:
                    province_list.append({
                        'id': province.id,
                        'name': province.name
                    })
                cache.set(
                    'province_list',
                    province_list,
                    constants.AREA_CACHE_EXPIRES)
            return http.JsonResponse(
                {'code': RETCODE.OK, 'province_list': province_list})

        sub_data = cache.get('area_' + area_id)
        if sub_data is None:
            try:
                districts = Areas.objects.get(id=area_id)
            except BaseException:
                return http.JsonResponse(
                    {'code': RETCODE.PARAMERR, 'errmsg': '地区编号无效'})
            else:
                subs_list = []
                sub_districts = districts.subs.all()
                for sub_district in sub_districts:
                    subs_list.append({
                        'id': sub_district.id,
                        'name': sub_district.name
                    })
                sub_data = {
                    'subs': subs_list
                }
                cache.set(
                    'area_' + area_id,
                    sub_data,
                    constants.AREA_CACHE_EXPIRES)
        return http.JsonResponse({'code': RETCODE.OK, 'sub_data': sub_data})
