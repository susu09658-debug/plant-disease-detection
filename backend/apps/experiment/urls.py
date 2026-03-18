from django.urls import path
from .views import (
    ExperimentMetricsView,
    ExperimentTrainCurvesView,
    ModelInfoView,
    TrainHistoryView,
    TrainConfigView,
)

urlpatterns = [
    path('metrics/', ExperimentMetricsView.as_view(), name='experiment_metrics'),
    path('curves/', ExperimentTrainCurvesView.as_view(), name='experiment_curves'),
    path('model-info/', ModelInfoView.as_view(), name='model_info'),
    path('train-history/', TrainHistoryView.as_view(), name='train_history'),
    path('train-config/', TrainConfigView.as_view(), name='train_config'),
]
