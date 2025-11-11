# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts'   # must be a STRING

urlpatterns = [
    path('', include('django.contrib.auth.urls')),  # gives you /accounts/login/, /logout/, etc.
    path('register/', views.register, name='register'),
]
