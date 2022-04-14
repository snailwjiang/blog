import hashlib
import json
import re
import time
import jwt
import random

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.core.cache import cache

# Create your views here.
from user.models import UserProfile
from tools.login_dec import login_check
from tools.sms import YunTongXin
from .tasks import task_test

class UserView(View):
    def get(self, request, username):
        if username:
            # 返回某个用户信息
            try:
                user = UserProfile.objects.get(username=username)
            except:
                result = {'code': 10103, 'error': '用户不存在'}
                return JsonResponse(result)
            keys = request.GET.keys()
            if keys:
                data = {}
                for k in keys:
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code': 200, 'username': user.username,
                          'data': data}
            else:
                result = {'code': 200, 'username': user.username,
                          'data': {'info': user.info,
                                   'sign': user.sign,
                                   'nickname': user.nikename,
                                   # str返回路径信息
                                   'avatar': str(user.avatar)}}
            return JsonResponse(result)

    def post(self, request):
        # 1获取json字符串
        json_str = request.body
        # 2反序列化
        py_obj = json.loads(json_str)
        # 获取每个数据
        username = py_obj['username']
        email = py_obj['email']
        phone = py_obj['phone']
        password_1 = py_obj['password_1']
        password_2 = py_obj['password_2']
        sms_num=py_obj['sms_num']
        # 效验逻辑问题
        # 用户名为空
        if not username:
            result = {'code': 10001, 'error': '用户名为空'}
            return JsonResponse(result)
        # 验证密码一致
        if password_1 != password_2:
            result = {'code': 10002, 'error': '两次密码不一致'}
            return JsonResponse(result)
        #验证码比较
        #从redis中获取验证吗
        cache_key = 'sms_%s' % phone
        code=str(cache.get(cache_key))
        print(code)
        #对比两个验证码
        if sms_num!=code:
            result={'code':10015,'error':'验证码错误'}
            return JsonResponse(result)

        # 用ma5加密密码
        password = hashlib.md5(password_1.encode()).hexdigest()
        # 添加进入数据库
        try:
            UserProfile.objects.create(username=username,
                                       email=email,
                                       phone=phone,
                                       password=password)
        except:
            reslut = {'code': 10003, 'error': '用户名重复'}
            return JsonResponse(reslut)
        # 注册成功生产token
        token = make_token(username)
        token = token.decode()
        return JsonResponse({'code': 200,
                             'username': username,
                             'data': {'token': token}})

    # 函数装饰器转换成方法装饰器
    @method_decorator(login_check)
    def put(self, request, username):
        # 1获取json字符串
        json_str = request.body
        # 2反序列化
        py_obj = json.loads(json_str)
        # 获取user对象
        user = request.myuser
        # 获取每个数据
        user.nikename = py_obj['nickname']
        user.sign = py_obj['sign']
        user.info = py_obj['info']
        # 5.保存save
        user.save()
        result = {'code': 200}
        return JsonResponse(result)


def make_token(username, exp=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'username': username,
               'exp': now + exp}
    return jwt.encode(payload, key)


@login_check
def user_avatar(request, username):
    if request.method != 'POST':
        return JsonResponse({'code': 10130, 'error': '请求方式必须是post'})
    # 修改用户头像
    # 1,查2,改3,上传(改数据库可能不成功，应该try)
    # 验证token
    user = request.myuser
    user.avatar = request.FILES['avatar']
    user.save()
    result = {'code': 200}
    return JsonResponse(result)


def sms_view(request):
    json_str = request.body;
    py_obj = json.loads(json_str)
    # 获取手机号,正则表达式验证
    phone = py_obj['phone']
    if is_phone(phone):
        # 缓存验证码
        # 生成键
        cache_key = 'sms_%s' % phone
        # 生成验证码
        code = random.randint(1000, 9999)
        #将验证码写入到redis中
        cache.set(cache_key,code,65)
        # 发送短信验证请求(同步)
        # x = YunTongXin(settings.SMS_ACCOUNT_ID,
        #                settings.SMS_ACCOUNT_TOKEN,
        #                settings.SMS_APP_ID,
        #                settings.SMS_TEMPLATE_ID)
        # 应该try或者完善sms报错情况
        # res = x.run(phone, code)
        # 发送短信验证请求(异步)
        task_test.delay(phone,code)
        result = {'code': 200, }
        return JsonResponse(result)
    else:
        result = {'code': 10011, 'error': '请输入正确手机格式'}
        return JsonResponse(result)


# 手机号是否正确
def is_phone(phone):
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, phone)
    if not res:
        return False
    return True
