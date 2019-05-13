from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU


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
