import json
from django_redis import get_redis_connection
from django import http
from django.shortcuts import render
from django.views import View

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsView(View):
    def post(self, request, ):
        # 接收
        sku_id = json.loads(request.body.decode()).get('sku_id')
        count = json.loads(request.body.decode()).get('count')
        # 验证
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        try:
            count = int(count)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号格式不对'})
        if count <= 0:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品数量不能为零或负数'})
        if count > sku.stock:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品数量超过上限'})
        # 处理
        user = request.user
        if user.is_authenticated:
            # 存入redis
            redis_conn = get_redis_connection('carts')
            redis_pl = redis_conn.pipeline()
            redis_pl.hset('carts%d' % user.id, sku_id, count)
            redis_pl.sadd('selected%d' % user.id, sku_id)
            redis_pl.execute()
        else:
            # 存入cookie
            pass
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

    def get(self, request):
        user = request.user
        carts = {}
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # redis_pl = redis_conn.pipeline()
            skus_counts = redis_conn.hgetall('carts%d' % user.id)
            skus_selected = redis_conn.smembers('selected%d' % user.id)
            # redis_pl.execute()
            for sku_id, count in skus_counts.items():
                carts[int(sku_id)] = {
                    'count': count,
                    'selected': sku_id in skus_selected,
                }

        else:
            pass
        # 转化成前端需要的格式
        cart_skus = []
        for sku_id, count_selected in carts.items():
            sku = SKU.objects.get(pk=sku_id)
            selected = count_selected['selected']
            count = int(count_selected['count'])
            cart_skus.append({
                'id': sku_id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': str(sku.price),
                'selected': str(selected),
                'count': count,
                'total_price': str(sku.price * count)
            })
        return render(request, 'cart.html', context={'cart_skus': cart_skus})

    def put(self, request):
        # 接收
        user = request.user
        sku_id = json.loads(request.body.decode()).get('sku_id')
        count = json.loads(request.body.decode()).get('count')
        selected = json.loads(request.body.decode()).get('selected', True)
        # 验证
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        try:
            count = int(count)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号格式不对'})
        if count <= 0:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品数量不能为零或负数'})
        if count > sku.stock:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品数量超过上限'})
        # 处理
        carts = {}
        if user.is_authenticated:
            # 修改redis
            redis_conn = get_redis_connection('carts')
            redis_pl = redis_conn.pipeline()
            redis_pl.hset('carts%d' % user.id, sku_id, count)
            if selected:
                redis_pl.sadd('selected%d' % user.id, sku_id)
            else:
                redis_pl.srem('selected%d' % user.id, sku_id)
            redis_pl.execute()
        else:
            # 修改cookie
            pass

        cart_sku = {
            'id': sku_id,
            'default_image_url': sku.default_image.url,
            'name': sku.name,
            'price': str(sku.price),
            'selected': str(selected),
            'count': count,
            'total_price': str(sku.price * count)
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})

    def delete(self, request):
        sku_id = json.loads(request.body.decode()).get('sku_id')
        if not all([sku_id]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hdel('carts%d' % user.id, sku_id)
        else:
            # 在cookie中删除
            pass

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})