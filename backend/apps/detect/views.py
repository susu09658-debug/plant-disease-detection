import os
import uuid
from pathlib import Path

from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.authentication import JWTAuthentication
from .models import DetectRecord
from .serializers import DetectRecordSerializer


class DetectUploadView(APIView):
    """图片上传与 YOLOv8 检测接口"""
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'code': 400, 'msg': '请上传图片文件'})

        # 保存原始图片
        uploads_dir = settings.MEDIA_ROOT / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(image_file.name)[1] or '.jpg'
        filename = f"upload_{uuid.uuid4().hex}{ext}"
        save_path = uploads_dir / filename
        with open(save_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        original_img_rel = f"uploads/{filename}"

        # 调用 YOLOv8 推理
        from utils.yolo_model import yolo_model
        result = yolo_model.detect(str(save_path))

        # 保存检测记录
        record = DetectRecord.objects.create(
            user=request.user,
            original_img=original_img_rel,
            result_img=result.get('result_image_path', original_img_rel),
            disease_name=result.get('disease_name', '未知'),
            plant_name=result.get('plant_name', ''),
            confidence=result.get('confidence', 0.0),
            bbox_data=result.get('bbox_data', []),
            detect_time=timezone.now(),
        )

        serializer = DetectRecordSerializer(record)
        return Response({
            'code': 200,
            'msg': '检测完成',
            'data': {
                **serializer.data,
                'original_img_url': request.build_absolute_uri(settings.MEDIA_URL + original_img_rel),
                'result_img_url': request.build_absolute_uri(
                    settings.MEDIA_URL + result.get('result_image_path', original_img_rel)
                ),
            }
        })


class DetectHistoryView(APIView):
    """获取当前用户的检测历史列表"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        keyword = request.query_params.get('keyword', '')

        queryset = DetectRecord.objects.filter(user=request.user).order_by('-detect_time')
        if keyword:
            queryset = queryset.filter(disease_name__icontains=keyword)

        total = queryset.count()
        start = (page - 1) * page_size
        records = queryset[start:start + page_size]
        serializer = DetectRecordSerializer(records, many=True)

        # 附加图片 URL
        data_list = []
        for item in serializer.data:
            item_dict = dict(item)
            item_dict['original_img_url'] = request.build_absolute_uri(
                settings.MEDIA_URL + item_dict['original_img']
            ) if item_dict.get('original_img') else ''
            item_dict['result_img_url'] = request.build_absolute_uri(
                settings.MEDIA_URL + item_dict['result_img']
            ) if item_dict.get('result_img') else ''
            data_list.append(item_dict)

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'total': total,
                'list': data_list,
                'page': page,
                'page_size': page_size,
            }
        })

    def delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'code': 400, 'msg': '缺少记录ID'})
        DetectRecord.objects.filter(id__in=ids, user=request.user).delete()
        return Response({'code': 200, 'msg': '删除成功'})


class DetectDetailView(APIView):
    """单条检测记录详情/删除"""
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        record = DetectRecord.objects.filter(id=pk, user=request.user).first()
        if not record:
            return Response({'code': 404, 'msg': '记录不存在'})
        serializer = DetectRecordSerializer(record)
        data = dict(serializer.data)
        data['original_img_url'] = request.build_absolute_uri(
            settings.MEDIA_URL + data['original_img']
        ) if data.get('original_img') else ''
        data['result_img_url'] = request.build_absolute_uri(
            settings.MEDIA_URL + data['result_img']
        ) if data.get('result_img') else ''
        return Response({'code': 200, 'msg': '查询成功', 'data': data})

    def delete(self, request, pk):
        record = DetectRecord.objects.filter(id=pk, user=request.user).first()
        if not record:
            return Response({'code': 404, 'msg': '记录不存在'})
        record.delete()
        return Response({'code': 200, 'msg': '删除成功'})


class DetectStatsView(APIView):
    """检测统计数据（首页仪表盘使用）"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        queryset = DetectRecord.objects.filter(user=request.user)
        total = queryset.count()

        # 各病害分布
        disease_dist = list(
            queryset.values('disease_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # 近7天检测趋势
        from datetime import timedelta, date
        today = date.today()
        trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = queryset.filter(detect_time__date=day).count()
            trend.append({'date': str(day), 'count': count})

        # 今日检测数
        today_count = queryset.filter(detect_time__date=today).count()

        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': {
                'total': total,
                'today_count': today_count,
                'disease_distribution': disease_dist,
                'weekly_trend': trend,
            }
        })
