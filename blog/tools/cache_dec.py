from django.core.cache import cache

from .login_dec import get_user_by_request
def topic_cache(expire):
    def _top_cache(func):
        def wrapper(request,*args,**kwargs):
            #判断是否是详情页,
            if 't_id' in request.GET.keys():
                return func(request,*args,**kwargs)
            vistor=get_user_by_request(request)
            author_id=kwargs['author_id']
            if vistor==author_id:
                #博主自己
                cache_key='topic_cache_self_%s'%(request.get_full_path())
            else:
                #非博主自己
                cache_key='topic_cache_%s'%(request.get_full_path())
            res =cache.get(cache_key)
            if res:
                print('--------redis cache in --------')
                return res
            res = func(request,*args,**kwargs)
            #将结果保持在缓存中
            cache.set(cache_key,res,expire)
            #返回结果
            return res
        return wrapper
    return _top_cache