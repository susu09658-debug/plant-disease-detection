from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DetectRecord
from .serializers import DetectRecordSerializer
from apps.user.models import User
from django.utils import timezone

# Create your views here.

class DetectUploadView(APIView):
    """
    图片上传与检测接口（模型推理部分预留）
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        original_img = request.data.get('original_img')
        # 这里应为图片上传与模型推理，暂时只做记录保存
        # TODO: 集成YOLOv11模型推理
        result_img = request.data.get('result_img', '')  # 预留
        disease_name = request.data.get('disease_name', '')  # 预留
        confidence = request.data.get('confidence', 0.0)  # 预留
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'code': 400, 'msg': '用户不存在'})
        record = DetectRecord.objects.create(
            user=user,
            original_img=original_img,
            result_img=result_img,
            disease_name=disease_name,
            confidence=confidence,
            detect_time=timezone.now()
        )
        return Response({'code': 200, 'msg': '检测记录已保存', 'data': DetectRecordSerializer(record).data})

class DetectHistoryView(APIView):
    """
    获取用户检测历史
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'code': 400, 'msg': '缺少用户ID'})
        records = DetectRecord.objects.filter(user_id=user_id).order_by('-detect_time')
        serializer = DetectRecordSerializer(records, many=True)
        return Response({'code': 200, 'msg': '查询成功', 'data': serializer.data})

    def delete(self, request):
        record_id = request.data.get('id')
        if not record_id:
            return Response({'code': 400, 'msg': '缺少记录ID'})
        DetectRecord.objects.filter(id=record_id).delete()
        return Response({'code': 200, 'msg': '删除成功'})
