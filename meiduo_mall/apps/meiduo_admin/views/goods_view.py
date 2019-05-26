from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from meiduo_admin.serializers.goods_serializers import SKUSerializer, GoodsCategorySerializer, SPUSimpleSerializer, \
    SPUSpecSerializer
from meiduo_admin.utils.page_num import PageNum
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification


class SKUView(ModelViewSet):
    serializer_class = SKUSerializer
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)


class SKUCategoryView(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = GoodsCategorySerializer


class SPUNameView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSimpleSerializer


class SPUSpecsView(ListAPIView):
    serializer_class = SPUSpecSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return SPUSpecification.objects.filter(spu_id=pk)
