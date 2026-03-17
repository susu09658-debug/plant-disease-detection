from django.urls import path
from .views import KnowledgeListView, KnowledgeManageView

urlpatterns = [
    path('list/', KnowledgeListView.as_view(), name='knowledge_list'),
    path('manage/', KnowledgeManageView.as_view(), name='knowledge_manage'),
]
