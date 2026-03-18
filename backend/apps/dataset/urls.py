from django.urls import path
from .views import (
    DatasetOverviewView,
    DatasetClassListView,
    DatasetSamplesView,
    DatasetSplitInfoView,
    DatasetValidateView,
)

urlpatterns = [
    path('overview/', DatasetOverviewView.as_view(), name='dataset_overview'),
    path('classes/', DatasetClassListView.as_view(), name='dataset_classes'),
    path('samples/', DatasetSamplesView.as_view(), name='dataset_samples'),
    path('split-info/', DatasetSplitInfoView.as_view(), name='dataset_split_info'),
    path('validate/', DatasetValidateView.as_view(), name='dataset_validate'),
]
