import logging
import random

import django_redis
from django import http
from django.shortcuts import render

from django.views import View

from identify import constants

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP

logger=logging.getLogger('django')

class ImageIdentify(View):
    def get(self, request, uuid):
        # 生成图形验证码
        text, code, image = captcha.generate_captcha()
        # 将验证码保存在redis中
        conn = django_redis.get_redis_connection('identification')
        # print(code)
        conn.setex(uuid, constants.IMAGE_CODE_EXPIRES, code)
        return http.HttpResponse(image, content_type='image/png')


class MessageIdentify(View):
    def get(self, request, mobile):
        image_code_cli = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')

        # 提取图形验证码
        conn = django_redis.get_redis_connection('identification')
        image_code_server = conn.get(image_code_id)

        if image_code_server is None:
            return http.JsonResponse({'code': 0, 'errmsg': '验证码已失效'})

        # 删除图形验证码
        try:
            conn.delete(image_code_id)
        except Exception as e:
            logger.error(e)

        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_cli.lower() != image_code_server.lower():
            return http.JsonResponse({'code': 0, 'errmsg': '验证码填写错误'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0,999999)
        # 保存验证码
        conn.setex(mobile,constants.Message_CODE_EXPIRES,sms_code)
        # 发送验证码
        CCP().send_template_sms(mobile, [sms_code, constants.Message_CODE_EXPIRES,], 1)
        return http.JsonResponse({'code': 0, 'errmsg': '短信发送成功'})

