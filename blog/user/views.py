import hashlib
import json
import time
import jwt

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings

# Create your views here.
from user.models import UserProfile
from tools.login_dec import login_check


class UserView(View):
    def get(self,request,username):
        if username:
            #返回某个用户信息
            try:
                user=UserProfile.objects.get(username=username)
            except:
                result={'code':10103,'error':'用户不存在'}
                return JsonResponse(result)
            keys=request.GET.keys()
            if keys:
                data={}
                for k in keys:
                    if k=='password':
                        continue
                    if hasattr(user,k):
                        data[k]=getattr(user,k)
                result={'code':200,'username':user.username,
                        'data':data}
            else:
                result={'code':200,'username':user.username,
                        'data':{'info':user.info,
                                'sign':user.sign,
                                'nikename':user.nikename,
                                #str返回路径信息
                                'avatar':str(user.avatar)}}
            return JsonResponse(result)

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

    #函数装饰器转换成方法装饰器
    @method_decorator(login_check)
    def put(self,request,username):
        # 1获取json字符串
        json_str = request.body
        # 2反序列化
        py_obj = json.loads(json_str)
        #获取user对象
        user=request.myuser
        # 获取每个数据
        user.nikename=py_obj['nickname']
        user.sign=py_obj['sign']
        user.info=py_obj['info']
        #5.保存save
        user.save()
        result={'code':200}
        return JsonResponse(result)

def make_token(username,exp=3600*24):
    key =settings.JWT_TOKEN_KEY
    now = time.time()
    payload={'username':username,
             'exp':now+exp}
    return jwt.encode(payload,key)

@login_check
def user_avatar(request,username):
    if request.method!='POST':
        return JsonResponse({'code':10130,'error':'请求方式必须是post'})
    #修改用户头像
    #1,查2,改3,上传(改数据库可能不成功，应该try)
    #验证token
    user = request.myuser
    user.avatar=request.FILES['avatar']
    user.save()
    result={'code':200}
    return JsonResponse(result)
