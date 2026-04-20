import os
import django

# 1. 设置 Django 环境（注意：把 'your_project_name' 替换为你实际的工程文件夹名字，也就是包含 settings.py 的那个文件夹名字）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 2. 启动 Django
django.setup()

# ================= 下面是你原来的代码 =================

import random
import string
from django.contrib.auth.hashers import make_password
# 注意：请将 'your_app_name' 替换为你实际的 app 名称，例如 'user'
from apps.user.models import User

def create_mock_users(num=50):
    users_to_create = []
    default_password = make_password('Test1234')

    for i in range(num):
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        username = f'test{i}{suffix}'
        second_digit = random.randint(3, 9)
        rest_digits = ''.join(random.choices(string.digits, k=9))
        phone = f'1{second_digit}{rest_digits}'
        nickname = f'测试用户{i+1}'

        user = User(
            username=username,
            password=default_password,
            phone=phone,
            nickname=nickname,
            is_admin=0,
            is_active=1
        )
        users_to_create.append(user)

    User.objects.bulk_create(users_to_create)
    print(f"✅ 成功批量生成 {num} 个普通用户！默认密码均为：Test1234")

if __name__ == '__main__':
    create_mock_users(50)