import logging
import random
import django_redis
from django import http
from django.shortcuts import render
from django.views import View
from identify import constants
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import ccp_sms_celery

logger = logging.getLogger('django')


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
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})

        # 删除图形验证码
        try:
            conn.delete(image_code_id)
        except Exception as e:
            logger.error(e)

        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_cli.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码填写错误'})

        # 校验短信验证码发送频率
        send_flag = conn.get('sendflag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码发送过于频繁'})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 保存验证码和sendflag(防止验证码发送过于频繁)
        pl = conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.Message_CODE_EXPIRES, sms_code)
        pl.setex('sendflag_%s' % mobile, constants.Send_SMS_INTERVAL, 1)
        pl.execute()
        # 发送验证码
        # CCP().send_template_sms(mobile, [sms_code, constants.Message_CODE_EXPIRES / 60], 1)
        ccp_sms_celery.delay(mobile, [sms_code, constants.Message_CODE_EXPIRES / 60], 1)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})
