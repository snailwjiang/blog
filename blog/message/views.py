import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.login_dec import login_check
from topic.models import Topic


@login_check
def message_view(request,topic_id):
    json_str=request.body
    py_obj=json.loads(json_str)
    content =py_obj['content']
    parent_id=py_obj.get('parent_id',0)
    #验证topic_id
    try:
        topic=Topic.objects.get(id=topic_id)
    except:
        result={'code':40100,'error':'topic error'}
        return JsonResponse(result)
    #获取登录用户
    user=request.myuser
    #添加数据
    Message.objects.create(topic=topic,
                          user_profile=user,
                          content=content,
                          parent_message=parent_id)
    result={'code':200}
    return JsonResponse(result)