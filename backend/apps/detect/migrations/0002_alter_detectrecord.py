# Generated migration for DetectRecord model enhancement

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detect', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detectrecord',
            name='plant_name',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='植物名称'),
        ),
        migrations.AddField(
            model_name='detectrecord',
            name='bbox_data',
            field=models.JSONField(blank=True, null=True, verbose_name='检测框数据'),
        ),
        migrations.AlterField(
            model_name='detectrecord',
            name='result_img',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='标注后图片路径'),
        ),
    ]
