from rest_framework import serializers
from goods.models import SKU, SKUSpecification


class SKUSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    specs = SKUSpecSerializer()
    spu = serializers.StringRelatedField()
    category = serializers.StringRelatedField()

    class Meta:
        model = SKU
        exclude = ['comments', 'default_image']
