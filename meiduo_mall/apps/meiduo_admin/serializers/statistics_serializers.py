from rest_framework import serializers
from goods.models import GoodsVisitCount


class CategoryVisitSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = GoodsVisitCount
        fields = ['count', 'category']
