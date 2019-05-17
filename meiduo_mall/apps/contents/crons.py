import os
from django.conf import settings
from django.shortcuts import render

from contents.models import ContentCategory
from meiduo_mall.utils.category import get_categories


def generate_static_index_html():
    categories = get_categories()
    # 广告展示
    content = {}
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        content[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'content': content
    }
    response = render(None, 'index.html', context)
    # 生成html字符串
    html_str = response.content.decode()
    # 写入文件
    path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(path, 'w') as f:
        f.write(html_str)
