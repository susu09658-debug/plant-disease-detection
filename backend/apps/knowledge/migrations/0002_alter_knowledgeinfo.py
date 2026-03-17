# Generated migration for KnowledgeInfo model enhancement

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledgeinfo',
            name='image_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='参考图片URL'),
        ),
        migrations.AddField(
            model_name='knowledgeinfo',
            name='severity',
            field=models.IntegerField(
                choices=[(1, '轻微'), (2, '较轻'), (3, '中等'), (4, '较重'), (5, '严重')],
                default=1,
                verbose_name='严重等级'
            ),
        ),
        migrations.AddField(
            model_name='knowledgeinfo',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间'),
        ),
        migrations.AddField(
            model_name='knowledgeinfo',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='knowledgeinfo',
            name='plant_name',
            field=models.CharField(db_index=True, max_length=30, verbose_name='植物名称'),
        ),
        migrations.AlterField(
            model_name='knowledgeinfo',
            name='disease_name',
            field=models.CharField(db_index=True, max_length=50, verbose_name='病害名称'),
        ),
    ]
