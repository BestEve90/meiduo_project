from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from meiduo_admin.serializers.goods_serializers import SKUSerializer, GoodsCategorySerializer, SPUSimpleSerializer, \
    SPUSpecSerializer, SPUSerializer
from meiduo_admin.utils.page_num import PageNum
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification


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


class SPUNameView(ListAPIView):
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
