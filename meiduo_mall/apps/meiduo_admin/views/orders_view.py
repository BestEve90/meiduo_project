from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.orders_serializer import OrderInfoSerializer
from orders.models import OrderInfo
from rest_framework.response import Response
from meiduo_admin.utils.page_num import PageNum
from rest_framework.decorators import action


class OrderView(ModelViewSet):
    pagination_class = PageNum
    serializer_class = OrderInfoSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        # data_dict = self.request.data
        # orderinfo = self.get_object()
        # serializer = self.get_serializer(orderinfo, data_dict)
        # if not serializer.is_valid():
        #     return Response('error':serializer.errors)   #  前端传的参数不全
        # serializer.save()
        # return Response(serializer.data)
        try:
            orderinfo = self.get_object()
        except:
            return Response({'error': '订单编号错误'})
        status = request.data.get('status')
        if status is None:
            return Response({'error': '状态值为空'})
        orderinfo.status = status
        orderinfo.save()
        return Response({
            'order_id': orderinfo.order_id,
            'status': status
        })
