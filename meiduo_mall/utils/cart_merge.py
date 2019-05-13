from django_redis import get_redis_connection

from meiduo_mall.utils import pickle_json


def cart_merge(request, response):
    user_id = request.user.id
    cart_str = request.COOKIES.get('cart')
    if cart_str is not None:
        cookie_carts = pickle_json.loads(cart_str)
        redis_conn = get_redis_connection('carts')
        set_sku_ids = redis_conn.smembers('selected%d' % user_id)
        redis_pl = redis_conn.pipeline()
        # 以cookie为准
        for sku_id, cart in cookie_carts.items():
            count = cart['count']
            selected = cart['selected']
            # 合并count
            redis_pl.hset('carts%d' % user_id, sku_id, count)
            # 合并selected
            if (sku_id not in set_sku_ids) and selected:
                redis_pl.sadd('selected%d' % user_id, sku_id, count)
            if (sku_id in set_sku_ids) and (not selected):
                redis_pl.srem('selected%d' % user_id, sku_id)
        redis_pl.execute()
    response.delete_cookie('cart')
