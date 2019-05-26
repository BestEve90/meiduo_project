from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.goods_serializers import SKUSerializer
from meiduo_admin.utils.page_num import PageNum
from goods.models import SKU


class SKUView(ModelViewSet):
    serializer_class = SKUSerializer
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)
