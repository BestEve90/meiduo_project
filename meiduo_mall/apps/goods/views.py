from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from goods import contants
from meiduo_mall.utils.category import get_categories
from .models import GoodsCategory, SKU, SKUSpecification
from meiduo_mall.utils.breadcrumb import get_breadcrumb
from copy import deepcopy


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
        sku_specifications = SKUSpecification.objects.filter(sku_id=sku_id)
        current_spec_options = {sku_specification.spec.name: sku_specification.option for sku_specification in
                                sku_specifications}

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
        for skui in spu.sku_set.all():
            skui_specifications = SKUSpecification.objects.filter(sku_id=skui.id)
            skui_spec_options = {skui_specification.spec.name: skui_specification.option for skui_specification in
                                 skui_specifications}
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
                url_spec_options[spec.name] = option # 所链接的sku的具体规格选项

                spec_options[spec.name].append({
                    'name': option.value,  # 选项名称
                    'selected': option == current_spec_options[spec.name],  # 是否当前商品的选项
                    'sku_id': skus_spec_options.get(tuple(url_spec_options.values()))  # 所链接的sku的id
                })

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'spu': spu,
            'spec_options': spec_options,

        }
        return render(request, 'detail.html', context)
