"""
创建管理员用户的 Django 管理命令。

用法:
    python manage.py create_admin --username admin --password admin123
    python manage.py create_admin --username admin --password admin123 --phone 13800000000
"""

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from apps.user.models import User


class Command(BaseCommand):
    help = '创建管理员用户 (Create an admin user)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='管理员用户名')
        parser.add_argument('--password', type=str, required=True, help='管理员密码')
        parser.add_argument('--phone', type=str, default='00000000000', help='手机号（可选）')
        parser.add_argument('--email', type=str, default='', help='邮箱（可选）')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        phone = options['phone']
        email = options['email']

        if len(password) < 6:
            raise CommandError('密码长度至少为 6 位')

        if User.objects.filter(username=username).exists():
            # 如果用户已存在，将其升级为管理员
            user = User.objects.get(username=username)
            user.is_admin = 1
            user.is_active = 1
            user.save(update_fields=['is_admin', 'is_active'])
            self.stdout.write(self.style.SUCCESS(
                f'用户 "{username}" 已存在，已升级为管理员'
            ))
            return

        User.objects.create(
            username=username,
            password=make_password(password),
            phone=phone,
            email=email or None,
            is_admin=1,
            is_active=1,
        )
        self.stdout.write(self.style.SUCCESS(
            f'管理员用户 "{username}" 创建成功'
        ))
