from django.urls import path

from . import views

urlpatterns=[
    path('<str:username>',views.UserView.as_view())
]