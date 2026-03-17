from django.urls import path
from .views import DetectUploadView, DetectHistoryView, DetectDetailView, DetectStatsView

urlpatterns = [
    path('upload/', DetectUploadView.as_view(), name='detect_upload'),
    path('history/', DetectHistoryView.as_view(), name='detect_history'),
    path('history/<int:pk>/', DetectDetailView.as_view(), name='detect_detail'),
    path('stats/', DetectStatsView.as_view(), name='detect_stats'),
]
