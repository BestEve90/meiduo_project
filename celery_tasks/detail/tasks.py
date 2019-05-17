import os
from django.conf import settings
from django.shortcuts import render
from meiduo_mall.utils.category import get_categories
from goods.models import SKU, SKUSpecification
from meiduo_mall.utils.breadcrumb import get_breadcrumb
from copy import deepcopy
from celery_tasks.main import celery_app


@celery_app.task(name='generate_static_detail_html')
def generate_static_detail_html(sku_id):
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
    response = render(None, 'detail.html', context)
    html_str = response.content.decode()
    path = os.path.join(settings.BASE_DIR, 'static/details/%d.html' % sku.id)
    with open(path, 'w') as f:
        f.write(html_str)
