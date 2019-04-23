import django_redis
from django import http
from django.shortcuts import render

from django.views import View

from identify import constants

from meiduo_mall.libs.captcha.captcha import captcha


class ImageIdentify(View):
    def get(self,request,uuid):
        # 生成图形验证码
        text,code,image = captcha.generate_captcha()
        # 将验证码保存在redis中
        conn = django_redis.get_redis_connection('image_code')
        conn.setex(uuid,constants.IMAGE_CODE_EXPIRES,code)
        return http.HttpResponse(image,content_type='image/png')
