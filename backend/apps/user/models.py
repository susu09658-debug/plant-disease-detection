from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=20, unique=True, verbose_name='用户ID')
    nickname = models.CharField(max_length=20, default='', verbose_name='用户昵称')
    password = models.CharField(max_length=128, verbose_name='加密密码')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    email = models.CharField(max_length=50, blank=True, null=True, verbose_name='邮箱')
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name='头像路径')
    is_admin = models.IntegerField(default=0, choices=((0, '普通'), (1, '管理员')), verbose_name='是否管理员')
    is_active = models.IntegerField(default=1, choices=((0, '禁用'), (1, '启用')), verbose_name='账号状态')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
