from django.conf import settings

from blog.celery import app
from tools.sms import YunTongXin


@app.task
def task_test(phone, code):
    x = YunTongXin(settings.SMS_ACCOUNT_ID,
                   settings.SMS_ACCOUNT_TOKEN,
                   settings.SMS_APP_ID,
                   settings.SMS_TEMPLATE_ID)
    res = x.run(phone, code)