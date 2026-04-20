from django.urls import path
from .views import KnowledgeListView, KnowledgeDetailView, KnowledgeManageView, ImageUploadView

urlpatterns = [
    path('list/', KnowledgeListView.as_view(), name='knowledge_list'),
    path('<int:pk>/', KnowledgeDetailView.as_view(), name='knowledge_detail'),
    path('manage/', KnowledgeManageView.as_view(), name='knowledge_manage'),
    path('manage/<int:pk>/', KnowledgeManageView.as_view(), name='knowledge_manage_detail'),
    path('upload/image/', ImageUploadView.as_view(), name='upload_image')
]
