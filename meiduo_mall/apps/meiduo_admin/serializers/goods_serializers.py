from django.conf import settings
from django.db import transaction
from fdfs_client.client import Fdfs_client
from rest_framework import serializers
from rest_framework.response import Response
from celery_tasks.detail.tasks import generate_static_detail_html

from goods.models import SKU, SKUSpecification, GoodsCategory, SPU, SpecificationOption, SPUSpecification, Brand, \
    SKUImage


class SKUSpecSerializer(serializers.ModelSerializer):
    '''商品规格序列化器'''

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    '''SKU序列化器'''
    specs = SKUSpecSerializer(many=True, read_only=True)  # 必须read_only? 写入数据库时不需要该数据,不read_only数据库报错,不支持nested fields可写
    spu = serializers.StringRelatedField(read_only=True)  # 必须read_only? 写入数据库时不需要该数据, 但不read_only也没出错
    spu_id = serializers.IntegerField()  # 必须单拎出来? 不然不存在? 对  无法进行序列化 写入数据库时没有该值,数据库报错
    category = serializers.StringRelatedField(read_only=True)  # 必须read_only? 写入数据库时不需要该数据, 但不read_only也没出错
    category_id = serializers.IntegerField()  # 必须单拎出来? 不然不存在? 对  无法进行序列化  写入数据库时没有该值,数据库报错

    class Meta:
        model = SKU
        exclude = ['comments', 'default_image']

    def create(self, validated_data):
        specs = self.context.get('request').data.get('specs')
        with transaction.atomic():
            spt = transaction.savepoint()
            try:
                sku = SKU.objects.create(**validated_data)
                for spec in specs:
                    SKUSpecification.objects.create(sku_id=sku.id, spec_id=spec['spec_id'], option_id=spec['option_id'])
            except:
                transaction.savepoint_rollback(spt)
                raise serializers.ValidationError({'error': '商品保存失败'})
            else:
                transaction.savepoint_commit(spt)
                generate_static_detail_html.delay(sku.id)
                return sku

    def update(self, instance, validated_data):
        specs = self.context.get('request').data.get('specs')
        with transaction.atomic():
            spt = transaction.savepoint()
            try:
                SKU.objects.filter(id=instance.id).update(**validated_data)
                for spec in specs:
                    SKUSpecification.objects.filter(sku=instance, spec_id=spec['spec_id']).update(option_id=spec['option_id'])
            except:
                transaction.savepoint_rollback(spt)
                raise serializers.ValidationError({'error': '商品修改失败'})
            else:
                transaction.savepoint_commit(spt)
                generate_static_detail_html.delay(instance.id)
                return instance


class SKUSimpleSerializer(serializers.ModelSerializer):
    '''SKU名称序列化器'''

    class Meta:
        model = SKU
        fields = ['id', 'name']


class GoodsCategorySerializer(serializers.ModelSerializer):
    '''商品类别序列化器'''

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSimpleSerializer(serializers.ModelSerializer):
    '''SPU商品名称序列化器'''

    class Meta:
        model = SPU
        fields = ['id', 'name']


class SpecsOptionSerializer(serializers.ModelSerializer):
    '''规格选项全序列化器'''
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'


class OptionsSerializer(serializers.ModelSerializer):
    '''规格选项简单序列化器'''

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecSerializer(serializers.ModelSerializer):
    '''SPU商品规格序列化器'''
    options = OptionsSerializer(many=True, read_only=True)
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'


class SpecSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPUSpecification
        fields = ['id', 'name']


class SPUSerializer(serializers.ModelSerializer):
    '''SPU序列化器'''
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        exclude = ['category1', 'category2', 'category3']


class BrandSerializer(serializers.ModelSerializer):
    '''品牌信息序列化器'''

    class Meta:
        model = Brand
        fields = ['id', 'name']


class SKUImageSerializer(serializers.ModelSerializer):
    '''SKU图片序列化器'''

    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']

    def create(self, validated_data):
        client = Fdfs_client(settings.FDFS_PATH)
        image_data = self.context.get('request').FILES.get('image')
        res = client.upload_by_buffer(image_data.read())
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})
        img = SKUImage.objects.create(sku=validated_data['sku'], image=res['Remote file_id'])
        generate_static_detail_html.delay(img.sku_id)
        return img

    def update(self, instance, validated_data):
        client = Fdfs_client(settings.FDFS_PATH)
        image_data = self.context.get('request').FILES.get('image')
        res = client.upload_by_buffer(image_data.read())
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        instance.sku = validated_data['sku']
        instance.image = res['Remote file_id']
        instance.save()
        generate_static_detail_html.delay(instance.sku_id)
        return instance
