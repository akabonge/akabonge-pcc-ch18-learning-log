from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                   # /
    path('topics/', views.topics, name='topics'),          # /topics/
    path('topics/<int:topic_id>/', views.topic, name='topic'),  # /topics/1/
]
