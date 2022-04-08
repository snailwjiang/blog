from celery import Celery
from django.conf import settings
import os

#为celery设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
#创建app
app=Celery('blog')
#配置应用
app.conf.update(
    #配置bocker
    BROKER_URL='redis://:@127.0.0.1:6379/1',

)
app.autodiscover_tasks(settings.INSTALLED_APPS)