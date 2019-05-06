from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.category import get_categories
from .models import Content,ContentCategory
import logging
logger=logging.getLogger('django')
class IndexView(View):
    def get(self, request):
        categories = get_categories()

        # 广告展示
        content={}
        content_categories=ContentCategory.objects.all()
        for content_category in content_categories:
            content[content_category.key]=content_category.content_set.filter(status=True).order_by('sequence')

        logger.info(content['index_lbt'][0].image.url)

        context = {
            'categories': categories,
            'content':content
        }
        return render(request, 'index.html', context)
