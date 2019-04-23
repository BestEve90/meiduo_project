import django_redis
from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from meiduo_mall import libs
from meiduo_mall.libs.captcha.captcha import captcha


class ImageIdentify(View):
    def get(self,request,uuid):
        text,code,image = captcha.generate_captcha()
        conn = django_redis.get_redis_connection('')
        return http.HttpResponse(image,content_type='image/png')
