"""
创建管理员用户的 Django 管理命令

使用方法:
    python manage.py create_admin --username admin --password admin123 --phone 13800000000
    python manage.py create_admin  # 交互式输入
"""

import getpass

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from apps.user.models import User


class Command(BaseCommand):
    help = '创建管理员用户（Create an admin user）'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='管理员用户名')
        parser.add_argument('--password', type=str, help='管理员密码')
        parser.add_argument('--phone', type=str, default='00000000000', help='手机号（默认: 00000000000）')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        phone = options['phone']

        # 交互式输入
        if not username:
            username = input('请输入管理员用户名: ').strip()
            if not username:
                self.stderr.write(self.style.ERROR('用户名不能为空'))
                return

        if not password:
            password = getpass.getpass('请输入管理员密码: ')
            if not password:
                self.stderr.write(self.style.ERROR('密码不能为空'))
                return
            password_confirm = getpass.getpass('请再次确认密码: ')
            if password != password_confirm:
                self.stderr.write(self.style.ERROR('两次输入的密码不一致'))
                return

        # 检查用户是否已存在
        existing = User.objects.filter(username=username).first()
        if existing:
            if existing.is_admin == 1:
                self.stdout.write(self.style.WARNING(
                    f'用户 "{username}" 已存在且已是管理员'))
                return
            # 将现有用户提升为管理员
            existing.is_admin = 1
            existing.save(update_fields=['is_admin'])
            self.stdout.write(self.style.SUCCESS(
                f'已将用户 "{username}" 提升为管理员'))
            return

        # 创建管理员用户
        User.objects.create(
            username=username,
            password=make_password(password),
            phone=phone,
            is_admin=1,
            is_active=1,
        )
        self.stdout.write(self.style.SUCCESS(
            f'管理员用户 "{username}" 创建成功！'))
        self.stdout.write('  登录后可在管理面板中管理用户和系统设置。')
