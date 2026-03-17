# apps/user/serializers.py
from rest_framework import serializers
from .models import User
import hashlib


class UserSerializer(serializers.ModelSerializer):
    """用于返回用户信息的序列化器（脱敏，不返回密码）"""

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'create_time', 'is_admin']


class RegisterSerializer(serializers.ModelSerializer):
    """用于处理用户注册请求的序列化器"""

    class Meta:
        model = User
        fields = ['username', 'password', 'phone']

    def create(self, validated_data):
        # 针对毕设级别的安全性，我们使用 MD5 对密码进行基础加密
        pwd = validated_data['password']
        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        validated_data['password'] = md5.hexdigest()

        # 将加密后的数据存入数据库
        return User.objects.create(**validated_data)