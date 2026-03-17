# backend/backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 接入用户模块，这会将请求代理到 apps/user/urls.py
    path('api/user/', include('apps.user.urls')),
    # 接入检测模块，这会将请求代理到 apps/detect/urls.py
    path('api/detect/', include('apps.detect.urls')),
    path('api/knowledge/', include('apps.knowledge.urls')),
]