import os
import uuid
from .models import KnowledgeInfo
from .serializers import KnowledgeInfoSerializer
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from utils.authentication import JWTAuthentication
from utils.permissions import IsAdminUser


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

        # --- 新增的核心处理逻辑 ---
        data_list = []
        for item in serializer.data:
            # 将 OrderedDict 转换为普通的 dict 以便修改
            item_dict = dict(item)

            image_url = item_dict.get('image_url')
            if image_url:
                # request.build_absolute_uri 非常智能：
                # 如果数据库存的是 '/media/xxx.jpg'，它会加上域名变成 'http://127.0.0.1:8000/media/xxx.jpg'
                # 如果数据库存的已经是完整的网络图片 'http://xxx...'，它会原样保留
                item_dict['image_url'] = request.build_absolute_uri(image_url)

            data_list.append(item_dict)

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'total': total,
                'list': data_list,  # 这里将 serializer.data 替换为处理后的 data_list
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


class ImageUploadView(APIView):
    """通用图片上传接口"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]  # 显式声明解析器以处理文件

    def post(self, request):
        file_obj = request.FILES.get('file')  # 对应 el-upload 默认的字段名 'file'

        if not file_obj:
            return Response({'code': 400, 'msg': '未检测到文件'})

        # 校验文件类型 (简单示例)
        if not file_obj.content_type.startswith('image/'):
            return Response({'code': 400, 'msg': '只能上传图片文件'})

        # 生成唯一文件名，防止覆盖
        ext = file_obj.name.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"

        # 保存路径: media/knowledge/xxx.jpg
        save_path = os.path.join('knowledge', filename)

        # 使用 Django 的 default_storage 保存文件
        actual_path = default_storage.save(save_path, file_obj)

        # 生成前端可访问的完整 URL
        # 1. 获取保存后的相对路径 (例如: /media/knowledge/abc.jpg)
        file_url = f"{settings.MEDIA_URL}{actual_path}"

        # 2. 【核心修改】使用 request 动态生成绝对地址
        # 这会将路径转换为 http://127.0.0.1:8000/media/knowledge/abc.jpg
        absolute_url = request.build_absolute_uri(file_url)

        return Response({
            'code': 200,
            'msg': '上传成功',
            'data': {'url': absolute_url}  # 返回给前端绝对地址
        })