#登录认证装饰器
import jwt
from django.conf import settings
from django.http import JsonResponse

from user.models import UserProfile


def login_check(fn):
    def warp(request,*args,**kwargs):
        token=request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result={'code':403,'error':'请登录'}
            return JsonResponse(result)
        #验证token,(要考虑token的安全性)
        try:
            payload=jwt.decode(token,settings.JWT_TOKEN_KEY)
        except Exception as e:
            print('the error is %s'% e)
            result={'code':403,'error':'请登录'}
            return JsonResponse(result)
        #payload获取私有声明
        username=payload['username']
        #根据用户名获取用户对象
        user = UserProfile.objects.get(username=username)
        #***将登录的用户对象添加到请求对象中
        request.myuser=user
        #调用装饰器修饰的函数
        return fn(request,*args,**kwargs)
    return warp

def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    # 验证token,(要考虑token的安全性)
    try:
        payload = jwt.decode(token, settings.JWT_TOKEN_KEY)
    except Exception as e:
        return None
    username = payload['username']
    return username