from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import KnowledgeInfo
from .serializers import KnowledgeInfoSerializer

# Create your views here.

class KnowledgeListView(APIView):
    """
    病害知识库列表与搜索
    """
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        if keyword:
            queryset = KnowledgeInfo.objects.filter(
                disease_name__icontains=keyword
            )
        else:
            queryset = KnowledgeInfo.objects.all()
        serializer = KnowledgeInfoSerializer(queryset, many=True)
        return Response({'code': 200, 'msg': '查询成功', 'data': serializer.data})

class KnowledgeManageView(APIView):
    """
    管理员：增删改病害知识库
    """
    def post(self, request):
        serializer = KnowledgeInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'msg': '新增成功', 'data': serializer.data})
        return Response({'code': 400, 'msg': '参数错误', 'data': serializer.errors})

    def put(self, request):
        kid = request.data.get('id')
        obj = KnowledgeInfo.objects.filter(id=kid).first()
        if not obj:
            return Response({'code': 404, 'msg': '未找到该病害信息'})
        serializer = KnowledgeInfoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'msg': '修改成功', 'data': serializer.data})
        return Response({'code': 400, 'msg': '参数错误', 'data': serializer.errors})

    def delete(self, request):
        kid = request.data.get('id')
        KnowledgeInfo.objects.filter(id=kid).delete()
        return Response({'code': 200, 'msg': '删除成功'})
