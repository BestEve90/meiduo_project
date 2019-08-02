#!/usr/bin/env python

import os
import django
import sys

sys.path.insert(0, '../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")
django.setup()

from goods.models import SKU
from celery_tasks.detail.tasks import generate_static_detail_html

if __name__ == '__main__':
    skus = SKU.objects.filter(is_launched=True)
    for sku in skus:
        print(sku.id)
        generate_static_detail_html(sku.id)
    print('ok')
