from rest_framework.response import Response
from rest_framework.views import APIView
from utils.authentication import JWTAuthentication
from utils.permissions import IsAdminUser
from .models import KnowledgeInfo
from .serializers import KnowledgeInfoSerializer


class KnowledgeListView(APIView):
    """病害知识库列表与搜索"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        plant_keyword = request.query_params.get('plant_name', '')
        disease_keyword = request.query_params.get('disease_name', '')
        keyword = request.query_params.get('keyword', '')

        queryset = KnowledgeInfo.objects.all().order_by('id')
        if keyword:
            queryset = queryset.filter(disease_name__icontains=keyword) | \
                       queryset.filter(plant_name__icontains=keyword)
        if plant_keyword:
            queryset = queryset.filter(plant_name__icontains=plant_keyword)
        if disease_keyword:
            queryset = queryset.filter(disease_name__icontains=disease_keyword)

        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start:start + page_size]
        serializer = KnowledgeInfoSerializer(items, many=True)
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'total': total,
                'list': serializer.data,
                'page': page,
                'page_size': page_size,
            }
        })


class KnowledgeDetailView(APIView):
    """知识库单条详情"""
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        obj = KnowledgeInfo.objects.filter(id=pk).first()
        if not obj:
            return Response({'code': 404, 'msg': '未找到该病害信息'})
        serializer = KnowledgeInfoSerializer(obj)
        return Response({'code': 200, 'msg': '查询成功', 'data': serializer.data})


class KnowledgeManageView(APIView):
    """管理员：增删改病害知识库"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = KnowledgeInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'msg': '新增成功', 'data': serializer.data})
        return Response({'code': 400, 'msg': '参数错误', 'data': serializer.errors})

    def put(self, request, pk):
        obj = KnowledgeInfo.objects.filter(id=pk).first()
        if not obj:
            return Response({'code': 404, 'msg': '未找到该病害信息'})
        serializer = KnowledgeInfoSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'msg': '修改成功', 'data': serializer.data})
        return Response({'code': 400, 'msg': '参数错误', 'data': serializer.errors})

    def delete(self, request, pk):
        KnowledgeInfo.objects.filter(id=pk).delete()
        return Response({'code': 200, 'msg': '删除成功'})
