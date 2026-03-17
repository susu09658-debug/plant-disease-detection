from django.db import models
from django.utils import timezone
from apps.user.models import User


class DetectRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='关联用户')
    original_img = models.CharField(max_length=255, verbose_name='原始图片路径')
    result_img = models.CharField(max_length=255, blank=True, null=True, verbose_name='标注后图片路径')
    disease_name = models.CharField(max_length=50, verbose_name='病害名称')
    plant_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='植物名称')
    confidence = models.FloatField(verbose_name='置信度')
    bbox_data = models.JSONField(blank=True, null=True, verbose_name='检测框数据')
    detect_time = models.DateTimeField(default=timezone.now, verbose_name='检测时间')

    class Meta:
        db_table = 'detect_record'
        verbose_name = '检测历史'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.disease_name}"
