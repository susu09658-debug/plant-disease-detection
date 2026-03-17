from django.db import models
from django.utils import timezone

class User(models.Model):
    username = models.CharField(max_length=20, verbose_name='用户名')
    password = models.CharField(max_length=100, verbose_name='加密密码')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    is_admin = models.IntegerField(default=0, choices=((0, '普通'), (1, '管理员')), verbose_name='是否管理员')

    class Meta:
        db_table = 'user_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username