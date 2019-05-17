import datetime
import json
import django_redis
from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from goods import contants
from meiduo_mall.utils.category import get_categories
from .models import GoodsCategory, SKU, SKUSpecification, GoodsVisitCount
from meiduo_mall.utils.breadcrumb import get_breadcrumb
from copy import deepcopy
from celery_tasks.detail.tasks import generate_static_detail_html

class ListView(View):
    def get(self, request, category_id, page):
        # 商品分类
        categories = get_categories()
        # 面包屑导航
        cat3 = GoodsCategory.objects.get(id=category_id)
        breadcrumb = get_breadcrumb(cat3)
        sort = request.GET.get('sort', 'default')
        skus = cat3.sku_set.filter(is_launched=True)
        if sort == 'price':
            skus = skus.order_by('price')
        elif sort == 'hot':
            skus = skus.order_by('-sales')
        else:
            skus = skus.order_by('-id')
        paginator = Paginator(skus, contants.NUM_PER_PAGE)
        page_skus = paginator.page(page)
        total_page = paginator.num_pages
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'category': cat3,
            'page_skus': page_skus,
            'page_num': page,
            'total_page': total_page,
            'sort': sort
        }

        return render(request, 'list.html', context)


class HotView(View):
    def get(self, request, category_id):
        # category = GoodsCategory.objects.get(id=category_id)
        # hot_skus = category.sku_set.filter(is_launched=True).order_by('-sales')[0:2]
        hot_skus = SKU.objects.filter(is_launched=True, category_id=category_id).order_by('-sales')[0:2]
        hot_sku_list = []
        for sku in hot_skus:
            hot_sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'hot_sku_list': hot_sku_list
        })


class DetailView(View):
    def get(self, request, sku_id):
        generate_static_detail_html.delay(sku_id)
        categories = get_categories()
        # 面包屑导航
        sku = SKU.objects.get(id=sku_id)
        category = sku.category
        breadcrumb = get_breadcrumb(category)
        # 标准商品spu信息
        spu = sku.spu

        # 当前sku具体规格选项
        '''
        current_spec_options={
            spec1.name:option,
            spec2.name:option,
            ...
        }
        '''
        sku_specs = SKUSpecification.objects.filter(sku_id=sku_id)
        current_spec_options = {sku_spec.spec_id: sku_spec.option_id for sku_spec in
                                sku_specs}

        # spu所有sku具体规格选项
        skus_spec_options = {}
        '''
        skus_spec_options = {
        (sku规格选项字典.value):sku.id
        }

        sku规格选项字典={
            spec1.name:option,
            spec2.name:option,
            ...
        }
        '''
        for skui in spu.sku_set.filter(is_launched=True):
            skui_specs = SKUSpecification.objects.filter(sku_id=skui.id)
            skui_spec_options = {skui_spec.spec_id: skui_spec.option_id for skui_spec in
                                 skui_specs}
            skus_spec_options[tuple(skui_spec_options.values())] = skui.id

        # 给前端返回的spu对应的规格选项
        spec_options = {}
        '''
        spec_options ={
            spu.spec1:[
                {
                    'name': spec.option.name,
                    'selected': ,
                    'sku_id': ,
                },
                {},
                ...
            ],
            spu.spec2:[],
            ...
        }
        '''
        specs = spu.specs.all()
        for spec in specs:
            options = spec.options.all()
            spec_options[spec.name] = []
            for option in options:
                url_spec_options = deepcopy(current_spec_options)
                url_spec_options[spec.id] = option.id  # 所链接的sku的具体规格选项

                spec_options[spec.name].append({
                    'name': option.value,  # 选项名称
                    'selected': option.id == current_spec_options[spec.id],  # 是否当前商品的选项
                    'sku_id': skus_spec_options.get(tuple(url_spec_options.values()))  # 所链接的sku的id
                })

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'spu': spu,
            'spec_options': spec_options,
            'category_id': category.id
        }
        return render(request, 'detail.html', context)


class VisitCountView(View):
    def post(self, request, category_id):
        # 查询访问记录
        t = datetime.datetime.now()
        today = '%d-%02d-%02d' % (t.year, t.month, t.day)
        try:
            good_visit = GoodsVisitCount.objects.get(category_id=category_id, date=today)
        except:
            # 没查到,新建
            GoodsVisitCount.objects.create(
                category_id=category_id,
                count=1,
            )
        else:
            # 查到了,数量增加
            good_visit.count += 1
            good_visit.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class HistoryView(View):
    def post(self, request):
        # 接收
        sku_id = json.loads(request.body.decode()).get('sku_id')
        # 验证
        # 非空
        if not all([sku_id]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品id不能为空'})
        # 有效性
        try:
            SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品id无效'})
        # 用户验证
        user = request.user
        if not user.is_authenticated:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '用户未登录'})
        # 处理
        # 连接redis,将sku_id以list的形式存储在redis中, key为'history_user_id'
        # 删除====>添加=====>截取5个
        redis_conn = django_redis.get_redis_connection('history')
        redis_pl = redis_conn.pipeline()
        redis_pl.lrem('history%d' % user.id, 0, sku_id)
        redis_pl.lpush('history%d' % user.id, sku_id)
        redis_pl.ltrim('history%d' % user.id, 0, 4)
        redis_pl.execute()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

    def get(self, request):
        # 接收
        user = request.user
        # 验证
        if not user.is_authenticated:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '用户未登录'})
        # 处理
        redis_conn = django_redis.get_redis_connection('history')
        sku_ids = redis_conn.lrange('history%d' % user.id, 0, -1)
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(pk=int(sku_id.decode()))
            skus.append({
                'id': sku_id.decode(),
                'name': sku.name,
                'price': sku.price,
                'default_image': sku.default_image.url
            })
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'skus': skus})
