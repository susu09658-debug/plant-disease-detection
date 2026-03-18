from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/detect/', include('apps.detect.urls')),
    path('api/knowledge/', include('apps.knowledge.urls')),
    path('api/experiment/', include('apps.experiment.urls')),
]

# 开发模式下提供 media 文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
