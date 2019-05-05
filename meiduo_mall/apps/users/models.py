from django.contrib.auth.models import AbstractUser
from django.db import models
from areas.models import Areas
from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', null=True, related_name='users', verbose_name='用户默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    user = models.ForeignKey(User, related_name='adresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='标题')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    province = models.ForeignKey(Areas, related_name='provinces', verbose_name='省')
    city = models.ForeignKey(Areas, related_name='cities', verbose_name='市')
    district = models.ForeignKey(Areas, related_name='districts', verbose_name='区县')
    place = models.CharField(max_length=100, verbose_name='详细地址')
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    tel = models.CharField(max_length=20, null=True, verbose_name='固定电话')
    email = models.CharField(max_length=50, null=True, verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        db_table = 'tb_addresses'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'receiver': self.receiver,
            'province': self.province.name,
            'city': self.city.name,
            'district': self.district.name,
            'place': self.place,
            'mobile': self.mobile,
            'tel': self.tel,
            'email': self.email
        }
