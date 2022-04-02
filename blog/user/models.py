import random

from django.db import models

def default_sign():
    signs=['IT精英','创业达人','人工智能专家','天才少年','yyds']
    return random.choice(signs)

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField('姓名', max_length=50,
                                primary_key=True)
    nikename = models.CharField('昵称', max_length=50)
    email = models.EmailField()
    password = models.CharField('密码', max_length=32)
    sign = models.CharField('个人签名', max_length=50,default=default_sign)
    info = models.CharField('个人描述', max_length=150,default='')
    avatar = models.ImageField(upload_to='avatar',
                               null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, default='')