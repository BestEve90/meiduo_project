import json
from django_redis import get_redis_connection
from django import http
from django.shortcuts import render
from django.views import View

from carts import constants
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils import pickle_json


class CartsView(View):
    def post(self, request, ):
        # 接收
        sku_id = json.loads(request.body.decode()).get('sku_id')
        count = json.loads(request.body.decode()).get('count')
        # 验证
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
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
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
        if user.is_authenticated:
            # 存入redis
            redis_conn = get_redis_connection('carts')
            redis_pl = redis_conn.pipeline()
            count_pre = redis_conn.hgetall('carts%d' % user.id).get(str(sku_id).encode(), 0)
            count += int(count_pre)
            redis_pl.hset('carts%d' % user.id, sku_id, count)
            redis_pl.sadd('selected%d' % user.id, sku_id)
            redis_pl.execute()
        else:
            # 存入cookie
            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                cart_dict = {}
            else:
                cart_dict = pickle_json.loads(cart_str)
            try:
                count_pre = cart_dict[sku_id].get('count')
                count += count_pre
            except:
                pass
            cart_dict[sku_id] = {'count': count, 'selected': True}
            response.set_cookie('cart', pickle_json.dumps(cart_dict), max_age=constants.CART_EXPIRES)
        return response

    def get(self, request):
        user = request.user
        carts = {}
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            skus_counts = redis_conn.hgetall('carts%d' % user.id)
            skus_selected = redis_conn.smembers('selected%d' % user.id)
            for sku_id, count in skus_counts.items():
                carts[int(sku_id)] = {
                    'count': count,
                    'selected': sku_id in skus_selected,
                }
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                carts = pickle_json.loads(cart_str)
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
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        try:
            count = int(count)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号格式不对'})
        if count <= 0:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品数量不能为零或负数'})
        if count > sku.stock:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '库存不足'})
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '选中状态无效'})
        # 处理
        cart_sku = {
            'id': sku_id,
            'default_image_url': sku.default_image.url,
            'name': sku.name,
            'price': str(sku.price),
            'selected': str(selected),
            'count': count,
            'total_price': str(sku.price * count)
        }  # 返回给前端,保证前端与后端一致
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})
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
            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '当前购物车没有数据'})
            cart_dict = pickle_json.loads(cart_str)
            cart_dict[sku_id] = {'count': count, 'selected': selected}
            response.set_cookie('cart', pickle_json.dumps(cart_dict), max_age=constants.CART_EXPIRES)
        return response

    def delete(self, request):
        sku_id = json.loads(request.body.decode()).get('sku_id')
        if not all([sku_id]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        try:
            sku = SKU.objects.get(pk=sku_id, is_launched=True)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        user = request.user
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hdel('carts%d' % user.id, sku_id)
            redis_conn.srem('selected%d' % user.id, sku_id)
        else:
            # 在cookie中删除
            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '当前购物车没有数据'})
            cart_dict = pickle_json.loads(cart_str)
            del cart_dict[sku_id]
            response.set_cookie('cart', pickle_json.dumps(cart_dict), max_age=constants.CART_EXPIRES)
        return response


class CartsSelectionView(View):
    def put(self, request):
        selected = json.loads(request.body.decode()).get('selected', True)
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '选中状态无效'})
        user = request.user
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            skus_counts = redis_conn.hgetall('carts%d' % user.id)
            if selected:
                for sku_id in skus_counts.keys():
                    redis_conn.sadd('selected%d' % user.id, sku_id)
            else:
                redis_conn.delete('selected%d' % user.id)
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str is None:
                return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '当前购物车没有数据'})
            cart_dict = pickle_json.loads(cart_str)
            for sku_id in cart_dict.keys():
                cart_dict[sku_id]['selected'] = selected
            response.set_cookie('cart', pickle_json.dumps(cart_dict), max_age=constants.CART_EXPIRES)
        return response


class CartsSimpleView(View):
    def get(self, request):
        user = request.user
        cart_dict={}
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            cart_dict = redis_conn.hgetall('carts%d' % user.id)
            cart_dict = {int(sku_id): int(count) for sku_id, count in cart_dict.items()}
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                cart_dict = pickle_json.loads(cart_str)
                cart_dict = {sku_id: cart['count'] for sku_id, cart in cart_dict.items()}
        cart_skus = []
        for sku_id, count in cart_dict.items():
            sku = SKU.objects.get(pk=sku_id)
            cart_skus.append({
                'name': sku.name,
                'count': count,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_skus': cart_skus})
