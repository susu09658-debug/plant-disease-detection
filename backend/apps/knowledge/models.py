from django.db import models
from django.utils import timezone


class KnowledgeInfo(models.Model):
    plant_name = models.CharField(max_length=30, db_index=True, verbose_name='植物名称')
    disease_name = models.CharField(max_length=50, db_index=True, verbose_name='病害名称')
    symptom = models.TextField(verbose_name='病害症状')
    treatment = models.TextField(verbose_name='防治方法')
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='参考图片URL')
    severity = models.IntegerField(
        default=1,
        choices=((1, '轻微'), (2, '较轻'), (3, '中等'), (4, '较重'), (5, '严重')),
        verbose_name='严重等级'
    )
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'knowledge_info'
        verbose_name = '病害知识库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.plant_name} - {self.disease_name}"
