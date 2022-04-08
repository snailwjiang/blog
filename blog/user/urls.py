from django.urls import path

from . import views

urlpatterns=[
    #注意sms的顺序，以免当做用户名解析
    path('sms',views.sms_view),
    path('<str:username>',views.UserView.as_view()),
    path('<str:username>/avatar',views.user_avatar),
]