from rest_framework import serializers
from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['name', 'default_image']


class OrderGoodsSerializer(serializers.ModelSerializer):
    sku = SKUSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['sku', 'count', 'price']


class OrderInfoSerializer(serializers.ModelSerializer):
    skus = OrderGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
