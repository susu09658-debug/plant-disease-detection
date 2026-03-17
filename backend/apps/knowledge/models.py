from django.db import models

class KnowledgeInfo(models.Model):
    plant_name = models.CharField(max_length=30, verbose_name='植物名称')
    disease_name = models.CharField(max_length=50, verbose_name='病害名称')
    symptom = models.TextField(verbose_name='病害症状')
    treatment = models.TextField(verbose_name='防治方法')

    class Meta:
        db_table = 'knowledge_info'
        verbose_name = '病害知识库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.plant_name} - {self.disease_name}"