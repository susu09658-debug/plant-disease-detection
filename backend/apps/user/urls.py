# apps/user/urls.py
from django.urls import path
from .views import CaptchaView, LoginView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('captcha/', CaptchaView.as_view(), name='captcha'),
]