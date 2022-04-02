import hashlib
import json
import time
import jwt

from django.http import JsonResponse
from django.views import View
from django.conf import settings

# Create your views here.
from user.models import UserProfile


class UserView(View):
    def get(self,request,username):
        print(username)
        if username:
            #返回某个用户信息
            try:
                user=UserProfile.objects.get(username=username)
            except:
                result={'code':10103,'error':'用户不存在'}
                return JsonResponse(result)
            result={'code':200,'username':user.username,
                    'data':{'info':user.info,
                            'sign':user.sign,
                            'nikename':user.nikename,
                            #str返回路径信息
                            'avatar':str(user.avatar)}}
            return JsonResponse(result)
        else:
            #返回所以用户信息
            pass

    def post(self,request):
        # 1获取json字符串
        json_str=request.body
        #2反序列化
        py_obj=json.loads(json_str)
        #获取每个数据
        username=py_obj['username']
        email = py_obj['email']
        phone = py_obj['phone']
        password_1 = py_obj['password_1']
        password_2 = py_obj['password_2']
        #效验逻辑问题
        #用户名为空
        if not username:
            result={'code':10001,'error':'用户名为空'}
            return JsonResponse(result)
        #验证密码一致
        if password_1!=password_2:
            result={'code':10002,'error':'两次密码不一致'}
            return JsonResponse(result)
        #用ma5加密密码
        password=hashlib.md5(password_1.encode()).hexdigest()
        #添加进入数据库
        try:
            UserProfile.objects.create(username=username,
                                       email=email,
                                       phone=phone,
                                      password=password)
        except:
            reslut={'code':10003,'error':'用户名重复'}
            return JsonResponse(reslut)
        #注册成功生产token
        token=make_token(username)
        token=token.decode()
        return JsonResponse({'code':200,
                             'username':username,
                             'data':{'token':token}})

def make_token(username,exp=3600*24):
    key =settings.JWT_TOKEN_KEY
    now = time.time()
    payload={'username':username,
             'exp':now+exp}
    return jwt.encode(payload,key)