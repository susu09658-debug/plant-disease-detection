from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用于返回用户信息的序列化器（脱敏，不返回密码）"""

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'phone', 'email', 'avatar', 'is_admin', 'is_active', 'create_time', 'last_login']


class RegisterSerializer(serializers.ModelSerializer):
    """用于处理用户注册请求的序列化器"""

    class Meta:
        model = User
        fields = ['username', 'nickname', 'password', 'phone']

    def create(self, validated_data):
        # 如果未提供昵称，默认使用用户ID作为昵称
        if not validated_data.get('nickname'):
            validated_data['nickname'] = validated_data['username']
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)
