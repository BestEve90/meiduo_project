from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.conf import settings
from alipay import AliPay
import os
from orders.models import OrderInfo
from django import http
from meiduo_mall.utils.response_code import RETCODE


class AlipayUrlView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单编号无效'})
        alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/alipay/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/alipay/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城-支付页面',
            return_url=settings.ALIPAY_RETURN_URL,
            notify_url=None
        )
        print(order_string)
        alipay_url = settings.ALIPAY_GATEWAY + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '', 'alipay_url': alipay_url})
