from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.response_code import RETCODE
from goods import contants
from meiduo_mall.utils.category import get_categories
from .models import GoodsCategory, SKU


class ListView(View):
    def get(self, request, category_id, page):
        categories = get_categories()
        cat3 = GoodsCategory.objects.get(id=category_id)
        cat2 = cat3.parent
        cat1 = cat2.parent
        breadcrumb = {
            'cat1': {
                'name': cat1.name,
                'url': cat1.goodschannel_set.all()[0].url
            },
            'cat2': cat2,
            'cat3': cat3
        }
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
