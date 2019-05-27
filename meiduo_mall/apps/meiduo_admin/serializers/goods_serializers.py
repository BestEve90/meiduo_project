from rest_framework import serializers
from goods.models import SKU, SKUSpecification, GoodsCategory, SPU, SpecificationOption, SPUSpecification


class SKUSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    specs = SKUSpecSerializer(many=True, read_only=True)  # 必须read_only?
    spu = serializers.StringRelatedField(read_only=True)  # 必须read_only?
    spu_id = serializers.IntegerField()  # 必须单拎出来? 不然不存在?
    category = serializers.StringRelatedField(read_only=True)  # 必须read_only?
    category_id = serializers.IntegerField()  # 必须单拎出来? 不然不存在?

    class Meta:
        model = SKU
        exclude = ['comments', 'default_image']


class GoodsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ['id', 'name']


class SpecsOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecSerializer(serializers.ModelSerializer):
    options = SpecsOptionSerializer(many=True)
    spu = serializers.StringRelatedField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'
