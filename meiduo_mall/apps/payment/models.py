from django.db import models
from meiduo_mall.utils.models import BaseModel
from orders.models import OrderInfo


class AlipayTradeNumber(BaseModel):
    order = models.ForeignKey(OrderInfo, related_name='alipays')
    trade_no=models.CharField(max_length=100)
    class Meta:
        db_table='tb_alipay'
