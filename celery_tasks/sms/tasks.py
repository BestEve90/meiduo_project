import time
from celery_tasks.main import celery_app
from meiduo_mall.libs.yuntongxun.ccp_sms import CCP


@celery_app.task(bind=True, name='ccp_sms_celery', retry_backoff=3)
def ccp_sms_celery(self, mobile, data, tmpid):
    try:
        # time.sleep(15)
        CCP().send_template_sms(mobile, data, tmpid)
    except Exception as e:
        raise self.retry(exc=e, max_retries=2)
