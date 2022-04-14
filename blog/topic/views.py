import json
import html

from django.core.cache import cache
from django.http import JsonResponse

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View

from message.models import Message
from tools.cache_dec import topic_cache
from tools.login_dec import login_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


class TopicView(View):
    # 清理缓存
    def clean_topic_cache(self, request):
        # 当博客内容发生改变时
        # 删除前，缓存键打印，确保键正确
        # cache.delete_many(健列表)
        keys_b = ['topic_cache_self_', 'topic_cache_']
        keys_m = request.path_info
        keys_p = ['', '?category=tec', '?category=no-tec']
        all_keys = []
        for key_b in keys_b:
            for key_p in keys_p:
                key = key_b + keys_m + key_p
                all_keys.append(key)
        print(all_keys)
        cache.delete_many(all_keys)

    # 博客详情返回值
    def maket_topic_res(self, author, author_topic, is_self):
        result = {'code': 200, 'data': {}}
        result['data']['nickname'] = author.nikename
        result['data']['title'] = author_topic.title
        result['data']['category'] = author_topic.category
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nikename
        result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')

        if is_self:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                              user_profile_id=author.username).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                              user_profile_id=author.username).last()

        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').last()
        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None
        result['data']['last_id'] = last_id
        result['data']['last_title'] = last_title
        result['data']['next_id'] = next_id
        result['data']['next_title'] = next_title

        # 留言显示
        all_msgs = Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list = []
        r_dict = {}
        msg_count = 0
        for msg in all_msgs:
            if msg.parent_message:
                # 回复
                r_dict.setdefault(msg.parent_message, [])
                r_dict[msg.parent_message].append({
                    'msg_id': msg.id,
                    'content': msg.content,
                    'publisher': msg.user_profile.nikename,
                    'publisher_avatar': str(msg.user_profile.avatar),
                    'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                # 评论
                msg_count += 1
                msg_list.append(
                    {'id': msg.id,
                     'content': msg.content,
                     'publisher': msg.user_profile.nikename,
                     'publisher_avatar': str(msg.user_profile.avatar),
                     'created_time': msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                     'reply': []
                     }
                )
        # 回复评论合二为一
        for m in msg_list:
            if m['id'] in r_dict:
                m['reply'] = r_dict[m['id']]

        result['data']['messages'] = msg_list
        result['data']['messages_count'] = msg_count
        return result

    # 博客列表返回值
    def make_topics_res(self, author, author_topics):
        topics_res = []
        # 遍历文章
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['author'] = author.nikename
            topics_res.append(d)
        res = {'code': 200, 'data': {}}
        res['data']['nickname'] = author.nikename
        res['data']['topics'] = topics_res
        return res

    @method_decorator(login_check)
    def post(self, request, author_id):

        # 1.获取前端数据
        json_str = request.body
        # 2.反序列号
        py_obj = json.loads(json_str)
        # {'content': content,
        # 'content_text': content_text,
        # 'limit': limit,
        # 'title': title,
        # 'category': category}
        title = py_obj['title']
        content_text = py_obj['content_text']
        limit = py_obj['limit']
        category = py_obj['category']
        content = py_obj['content']
        # 3.数据效验
        if not title:
            result = {'code': 20001, 'error': '标题不允许为空'}
            return JsonResponse(result)
        elif not content_text:
            result = {'code': 20002, 'error': '内容不允许为空'}
            return JsonResponse(result)
        elif limit not in ['public', 'private']:
            result = {'code': 20003, 'error': '权限错误'}
            return JsonResponse(result)
        elif category not in ['tec', 'no-tec']:
            result = {'code': 20004, 'error': '分类错误'}
            return JsonResponse(result)
        introduce = content_text[:20]
        # 4.转义，抵御XSS攻击,对标题做转义
        title = html.escape(title)
        # 5,文章作者，request.myuser
        user = request.myuser
        # 6.添加到数据库
        Topic.objects.create(title=title,
                             category=category,
                             limit=limit,
                             content=content,
                             introduce=introduce,
                             user_profile=user)
        # 发表博客，博客列表就会发生变化，所以需要清理缓存
        self.clean_topic_cache(request)
        result = {'code': 200, 'username': user.username}
        return JsonResponse(result)

    @method_decorator(topic_cache(600))
    def get(self, request, author_id):
        print('--------------view-----------')
        # .根据author_id获取博客博主
        try:
            author = UserProfile.objects.get(username=author_id)
        except:
            result = {'code': 20004, 'error': '该用户不存在'}
            return JsonResponse(result)
        # 获取访问者，可以是游客
        vistor = get_user_by_request(request)
        # 获取文章id
        t_id = request.GET.get('t_id')
        # 定义变量，
        # 是否博主本人
        is_self = False
        if t_id:
            if vistor == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id,
                                                     user_profile_id=author_id)
                except:
                    result = {'code': 30104, 'error': '文章标题错误'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id,
                                                     user_profile_id=author_id,
                                                     limit='public')
                except:
                    result = {'code': 30104, 'error': '文章标题错误'}
                    return JsonResponse(result)
            res = self.maket_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            # 分类问题
            category = request.GET.get('category', '')
            # 定义变量，默认不饿分类
            filer_category = False
            if category in ['tec', 'no-tec']:
                filer_category = True
            if vistor == author_id:
                if filer_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         category=category)
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id)
            else:
                if filer_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         category=category,
                                                         limit='public')

                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         limit='public')
            result = self.make_topics_res(author, author_topics)
            return JsonResponse(result)
