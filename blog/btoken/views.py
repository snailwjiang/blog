import hashlib
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from user.models import UserProfile
from user.views import make_token


class TokenView(View):
    def post(self ,request):
        #接收json字符串
        json_str=request.body
        #反序列化获得json对象
        py_obj=json.loads(json_str)
        #获取信息
        username=py_obj['username']
        password=py_obj['password']
        #用try获取用户信息,
        try:
            user_obj=UserProfile.objects.get(username=username)
            #验证MD5密码
        except Exception as e:
            print('this is error %s'%e)
            return JsonResponse({'code':10005,'error':'用户名或密码错误'})
        password_h = hashlib.md5(password.encode()).hexdigest()
        #验证密码
        if password_h != user_obj.password:
            return JsonResponse({'code':10006,'error':'用户名或密码错误'})
        #成功，生产token
        token=make_token(username)
        #防止生产字节串报错
        token=token.decode()
        return JsonResponse({'code':200,
                             'username':username,
                             'data':{'token':token}})