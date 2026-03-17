from django.urls import path
from .views import DetectUploadView, DetectHistoryView

urlpatterns = [
    path('upload/', DetectUploadView.as_view(), name='detect_upload'),
    path('history/', DetectHistoryView.as_view(), name='detect_history'),
]
