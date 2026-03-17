from django.db import models
from django.utils import timezone
from apps.user.models import User  # 引入 User 模型作为外键

class DetectRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='关联用户')
    original_img = models.CharField(max_length=255, verbose_name='原始图片路径')
    result_img = models.CharField(max_length=255, verbose_name='标注后图片路径')
    disease_name = models.CharField(max_length=50, verbose_name='病害名称')
    confidence = models.FloatField(verbose_name='置信度')
    detect_time = models.DateTimeField(default=timezone.now, verbose_name='检测时间')

    class Meta:
        db_table = 'detect_record'
        verbose_name = '检测历史'
        verbose_name_plural = verbose_name