from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.conf import settings
from alipay import AliPay
import os
from orders.models import OrderInfo
from django import http
from meiduo_mall.utils.response_code import RETCODE
from .models import AlipayTradeNumber


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


class AlipaySuccessView(LoginRequiredMixin, View):
    def get(self, request):
        '''
        http://www.meiduo.com/payment/status/?
        charset=utf-8
        out_trade_no=20190516140710252920000000006
        method=alipay.trade.page.pay.return
        total_amount=11388.00
        sign=B3WYg6mGwudrwtFoWhVaoIaSe%2BizqbQe%2F1bfKhNTrJNt8n6EB719GBAwR674WAgFDYbGjlrV%2BBKXDZakgtTvxmw3oL8q2Kx7TomZTIckko25mj%2FEOWEC3DO6RBhxoY0wsp4W4VmsGRVSoJ8krncefmYicdhYNTMVhW6X%2FqR0dsqaYqLt4%2FkT0Ok2lPRvs3Taqw3bMmmvoFXA4gamzJJdfA94F3q9fZv%2FSYn84vfwRTKXpFEha09u%2BWMv5ymsHfKpAXUnMcfMRIukDAnt2Uh3ZxI7kYfSrCOUiM36bzLLERXZITbDRJbGYQurMPhfXmQlAvul%2B0Cs2VN8m0hBkCwd7Q%3D%3D
        trade_no=2019051722001459121000008763
        auth_app_id=2016092900623100
        version=1.0
        app_id=2016092900623100
        sign_type=RSA2
        seller_id=2088102177790709
        timestamp=2019-05-17+08%3A42%3A10
        '''
        # 验证是否支付成功
        alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/alipay/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/payment/alipay/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        param_dict = request.GET.dict()
        signature = param_dict.pop('sign')
        success = alipay.verify(param_dict, signature)
        if not success:
            return http.HttpResponse('支付失败')
        # 保存订单号和支付流水号
        trade_no = param_dict.get('trade_no')
        out_trade_no = param_dict.get('out_trade_no')
        AlipayTradeNumber.objects.create(
            order_id=out_trade_no,
            trade_no=trade_no,
        )
        # 修改订单状态
        OrderInfo.objects.filter(pk=out_trade_no).update(status=2)
        # 返回成功支付页面
        return render(request, 'pay_success.html', {'trade_no':trade_no})
