# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-05-10 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodsVisitCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('count', models.IntegerField(default=0, verbose_name='访问量')),
                ('date', models.DateField(auto_now_add=True, verbose_name='统计日期')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='goods.GoodsCategory', verbose_name='商品分类')),
            ],
            options={
                'verbose_name_plural': '分类商品访问量',
                'db_table': 'tb_goods_visit',
                'verbose_name': '分类商品访问量',
            },
        ),
    ]
