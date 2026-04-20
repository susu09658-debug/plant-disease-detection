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
from datetime import timedelta, datetime, time

class DetectUploadView(APIView):
    """图片上传与 YOLOv11 检测接口（支持选择不同模型）"""
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'code': 400, 'msg': '请上传图片文件'})

        # 获取用户选择的模型（可选）
        model_key = request.data.get('model_key', None) or None

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

        # 调用 YOLOv11 推理（支持模型选择）
        from utils.yolo_model import yolo_model
        result = yolo_model.detect(str(save_path), model_key=model_key)

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
                'model_used': result.get('model_used', ''),
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

        # 获取当前时间的本地化日期，避免时区偏差
        today = timezone.localtime().date()
        trend = []

        for i in range(6, -1, -1):
            target_date = today - timedelta(days=i)

            # 构造一天的起点 (00:00:00) 和终点 (23:59:59)
            start_datetime = timezone.make_aware(datetime.combine(target_date, time.min))
            end_datetime = timezone.make_aware(datetime.combine(target_date, time.max))

            # 使用 range 范围查询替代原先的 __date 查询
            count = queryset.filter(detect_time__range=(start_datetime, end_datetime)).count()
            trend.append({'date': str(target_date), 'count': count})

        # 今日检测数 (同样修改为范围查询)
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        # 只要大于等于今天的 00:00:00 即可
        today_count = queryset.filter(detect_time__gte=today_start).count()

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


class DetectModelsView(APIView):
    """获取可用检测模型列表"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        from utils.yolo_model import YOLOModel
        models = YOLOModel.get_available_models()
        return Response({
            'code': 200,
            'msg': '查询成功',
            'data': models,
        })
