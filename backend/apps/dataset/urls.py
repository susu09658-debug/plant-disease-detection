from django.urls import path
from .views import (
    DatasetOverviewView,
    DatasetClassListView,
    DatasetSamplesView,
    DatasetSplitInfoView,
    DatasetValidateView,
    DatasetListView,  # 👈 1. 把新视图加到这里的导入列表里
)

urlpatterns = [
    # 2. 路径改成 'list/'，并且直接用 DatasetListView
    path('list/', DatasetListView.as_view(), name='dataset_list'),

    path('overview/', DatasetOverviewView.as_view(), name='dataset_overview'),
    path('classes/', DatasetClassListView.as_view(), name='dataset_classes'),
    path('samples/', DatasetSamplesView.as_view(), name='dataset_samples'),
    path('split-info/', DatasetSplitInfoView.as_view(), name='dataset_split_info'),
    path('validate/', DatasetValidateView.as_view(), name='dataset_validate'),
]