import json
from datetime import datetime
import time
from django.db import transaction
from meiduo_mall.utils.response_code import RETCODE
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU
from .models import OrderInfo, OrderGoods


class PlaceOrderView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # 查询用户收货地址
        default_address_id = user.default_address_id
        address_list = Address.objects.filter(is_deleted=False, user_id=user.id)

        # 查询购物车已勾选商品
        redis_conn = get_redis_connection('carts')
        selected_cart_dict = redis_conn.hgetall('carts%d' % user.id)
        selected_cart_dict = {int(sku_id): int(count) for sku_id, count in selected_cart_dict.items()}
        selected_sku_ids = redis_conn.smembers('selected%d' % user.id)
        selected_sku_ids = [int(sku_id) for sku_id in selected_sku_ids]
        total_count = 0
        total_money = 0
        selected_cart_skus = []
        for sku_id in selected_sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            count = selected_cart_dict[sku_id]
            total_count += count
            total_amount = sku.price * selected_cart_dict[sku_id]
            total_money += total_amount
            selected_cart_skus.append({
                'id': sku_id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
                'count': count,
                'total_amount': total_amount,
            })
        freight = 10  # 运费
        total_pay = total_money + freight
        context = {
            'default_address_id': default_address_id,
            'address_list': address_list,
            'selected_cart_skus': selected_cart_skus,
            'freight': freight,
            'total_count': total_count,
            'total_money': total_money,
            'total_pay': total_pay
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        address_id = json.loads(request.body.decode()).get('address_id')
        pay_method = json.loads(request.body.decode()).get('pay_method')
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            address = Address.objects.get(is_deleted=False, pk=address_id, user_id=user.id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '地址无效'})
        if pay_method not in ['1', '2']:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '支付方式无效'})
        with transaction.atomic():
            sid = transaction.savepoint()
            # 创建订单
            now = datetime.now()
            order_id = '%s%09d' % (now.strftime('%Y%m%d%H%M%S'), user.id)
            total_count = 0
            total_amount = 0
            freight = 10
            if pay_method == '1':
                status = 2
            else:
                status = 1
            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user_id=user.id,
                    address_id=address_id,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=int(pay_method),
                    status=status
                )
                # 查询购物车已勾选商品信息
                redis_conn = get_redis_connection('carts')
                cart_dict = redis_conn.hgetall('carts%d' % user.id)
                cart_dict = {int(sku_id): int(count) for sku_id, count in cart_dict.items()}
                cart_selected = redis_conn.smembers('selected%d' % user.id)
                cart_selected = [int(sku_id) for sku_id in cart_selected]
                if not cart_selected:
                    transaction.savepoint_rollback(sid)
                    return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单列表为空'})
                for sku_id in cart_selected:
                    count = cart_dict[sku_id]
                    sku = SKU.objects.get(pk=sku_id)
                    if count > sku.stock:
                        transaction.savepoint_rollback(sid)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                    time.sleep(5)
                    # 修改库存和销量
                    sku.stock -= count
                    sku.sales += count
                    sku.save()
                    # 创建订单商品
                    OrderGoods.objects.create(
                        order_id=order_id,
                        sku_id=sku_id,
                        count=count,
                        price=sku.price
                    )
                    # 修改订单总金额和订单总数
                    total_count += count
                    total_amount += sku.price * count
                order.total_count = total_count
                order.total_amount = total_amount
                order.save()
            except:
                transaction.savepoint_rollback(sid)
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单提交失败'})
            transaction.savepoint_commit(sid)

        # 删除购物车中选中商品
        redis_conn.hdel('carts%d' % user.id, *cart_selected)
        redis_conn.delete('selected%d' % user.id)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '', 'order_id': order_id})
