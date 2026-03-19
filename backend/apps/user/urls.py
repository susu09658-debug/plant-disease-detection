from django.urls import path
from .views import (
    CaptchaView, LoginView, RegisterView, LogoutView,
    ProfileView, PasswordView, ResetPasswordView, AdminUserListView, AdminUserDetailView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('captcha/', CaptchaView.as_view(), name='captcha'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password/', PasswordView.as_view(), name='password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
