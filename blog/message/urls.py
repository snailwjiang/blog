from django.urls import path

from message import views

urlpatterns=[

    path('<str:topic_id>',views.message_view),
]