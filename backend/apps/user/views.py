# apps/user/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, UserSerializer
import hashlib


class RegisterView(APIView):
    """用户注册接口"""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 200, "msg": "注册成功", "data": None})
        return Response({"code": 400, "msg": "参数错误", "data": serializer.errors})


class LoginView(APIView):
    """用户登录接口"""

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"code": 400, "msg": "用户名或密码不能为空"})

        # 将前端传来的明文密码进行同样的 MD5 加密，再与数据库比对
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        hashed_password = md5.hexdigest()

        # 查询数据库比对账号密码
        user = User.objects.filter(username=username, password=hashed_password).first()

        if user:
            # 登录成功，返回用户信息及一个简易的身份凭证(Token)
            serializer = UserSerializer(user)
            return Response({
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "token": f"user_token_{user.id}",  # 简易Token，前端可存入 localStorage
                    "user_info": serializer.data
                }
            })

        return Response({"code": 401, "msg": "用户名或密码错误"})