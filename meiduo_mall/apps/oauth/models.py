from django.db import models


# Create your models here.
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class OAuthQQUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    open_id = models.CharField(max_length=64, verbose_name='openid', db_index=True)
    class Meta:
        db_table='tb_oauth_qq'
        verbose_name='QQ登录用户数据'
        verbose_name_plural=verbose_name

