from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from meiduo_admin.serializers.goods_serializers import SKUSerializer, GoodsCategorySerializer, SPUSimpleSerializer, \
    SPUSpecSerializer, SPUSerializer, BrandSerializer, SpecsOptionSerializer, SpecSimpleSerializer, SKUImageSerializer, \
    SKUSimpleSerializer
from meiduo_admin.utils.page_num import PageNum
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification, Brand, SpecificationOption, SKUImage
from rest_framework.response import Response
from fdfs_client.client import Fdfs_client


class SKUView(ModelViewSet):
    '''SKU的增删改查'''
    serializer_class = SKUSerializer
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)


class SKUCategoryView(ListAPIView):
    '''获取所有三级商品类别'''
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = GoodsCategorySerializer


class SPUSimpleView(ListAPIView):
    '''获取所有SPU名称'''
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleSerializer


class SPUSpecsView(ListAPIView):
    '''获取某一SPU对应的所有规格信息'''
    serializer_class = SPUSpecSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return SPUSpecification.objects.filter(spu_id=pk)


class SPUView(ModelViewSet):
    '''SPU表的增删改查'''
    pagination_class = PageNum
    serializer_class = SPUSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SPU.objects.all()
        else:
            return SPU.objects.filter(name__contains=keyword)


class BrandView(ListAPIView):
    '''获取品牌信息'''
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ChannelView(ListAPIView):
    '''获取一级分类信息'''
    queryset = GoodsCategory.objects.filter(parent_id__isnull=True)
    serializer_class = GoodsCategorySerializer


class ChannelsView(APIView):
    '''获取二级和三级分类信息'''

    def get(self, request, pk):
        sub_cats = GoodsCategory.objects.filter(parent_id=pk)
        ser = GoodsCategorySerializer(sub_cats, many=True)
        return Response({'subs': ser.data})


class GoodSpecsView(ModelViewSet):
    '''商品规格表的增删改查'''
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecSerializer
    pagination_class = PageNum


class OptionsView(ModelViewSet):
    '''规格选项表的增删改查'''
    queryset = SpecificationOption.objects.all()
    serializer_class = SpecsOptionSerializer
    pagination_class = PageNum


class SpecsSimpleView(ListAPIView):
    '''获取规格名称信息'''
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSimpleSerializer


class SKUImagesView(ModelViewSet):
    '''SKU图片表的增删改查'''
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageSerializer
    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        client = Fdfs_client('/home/python/Desktop/meiduo_mall/meiduo_mall/utils/fastdfs/client.conf')
        data = request.FILES.get('image')
        res = client.upload_by_buffer(data.read())
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        image_url = res['Remote file_id']
        sku_id = request.data.get('sku')[0]
        img = SKUImage.objects.create(sku_id=sku_id, image=image_url)
        return Response({
            'id': img.id,
            'sku': sku_id,
            'image': img.image.url
        },
            status=201)


class SKUSimpleView(ListAPIView):
    '''获取SKU名称'''
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleSerializer
