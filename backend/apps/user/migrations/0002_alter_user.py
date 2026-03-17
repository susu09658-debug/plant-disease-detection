# Generated migration for User model enhancement

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='邮箱'),
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='头像路径'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.IntegerField(choices=[(0, '禁用'), (1, '启用')], default=1, verbose_name='账号状态'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间'),
        ),
        migrations.AddField(
            model_name='user',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=20, unique=True, verbose_name='用户名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, verbose_name='加密密码'),
        ),
    ]
