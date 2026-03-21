import base64
import hashlib
import io
import os
import random
import string

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.authentication import JWTAuthentication
from utils.jwt_utils import generate_token
from utils.permissions import IsAdminUser

from .models import User
from .serializers import RegisterSerializer, UserSerializer


def _make_captcha_text(length=4):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))


def _make_captcha_image(text):
    width, height = 120, 40
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for i, ch in enumerate(text):
        x = 10 + i * 25
        y = random.randint(8, 14)
        draw.text((x, y), ch, fill=(20, 60, 120), font=font)

    for _ in range(6):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(170, 170, 170), width=1)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{image_b64}"


def _check_captcha(token, user_input, delete_after_verify=False):
    if not token or not user_input:
        return False
    expected = cache.get(f"captcha:{token}")
    if not expected:
        return False
    matched = expected.lower() == str(user_input).strip().lower()
    if matched and delete_after_verify:
        cache.delete(f"captcha:{token}")
    return matched


class CaptchaView(APIView):
    """图形验证码接口"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        text = _make_captcha_text()
        token = hashlib.md5(f"{text}-{random.random()}".encode("utf-8")).hexdigest()
        cache.set(f"captcha:{token}", text, timeout=300)
        image = _make_captcha_image(text)
        return Response({
            "code": 200,
            "msg": "获取验证码成功",
            "data": {
                "token": token,
                "image": image,
            },
        })


class RegisterView(APIView):
    """用户注册接口"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 200, "msg": "注册成功", "data": None})
        return Response({"code": 400, "msg": "参数错误", "data": serializer.errors})


class LoginView(APIView):
    """用户登录接口"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        captcha = request.data.get('captcha')
        captcha_token = request.data.get('captcha_token')

        if not username or not password:
            return Response({"code": 400, "msg": "用户名或密码不能为空"})

        if not _check_captcha(captcha_token, captcha, delete_after_verify=True):
            return Response({"code": 400, "msg": "图形验证码错误或已过期"})

        user = User.objects.filter(username=username).first()
        if not user or not check_password(password, user.password):
            return Response({"code": 401, "msg": "用户名或密码错误"})

        if user.is_active == 0:
            return Response({"code": 403, "msg": "账号已被禁用，请联系管理员"})

        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        token = generate_token(user.id, user.username, user.is_admin)
        serializer = UserSerializer(user)
        return Response({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": token,
                "user_info": serializer.data,
            },
        })


class LogoutView(APIView):
    """用户登出接口"""
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        return Response({"code": 200, "msg": "登出成功", "data": None})


class ProfileView(APIView):
    """个人信息接口"""
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"code": 200, "msg": "获取成功", "data": serializer.data})

    def put(self, request):
        user = request.user
        phone = request.data.get('phone')
        email = request.data.get('email')
        username = request.data.get('username')

        update_fields = []

        if username and username != user.username:
            if len(username) < 2 or len(username) > 20:
                return Response({"code": 400, "msg": "用户名长度需为2~20个字符"})
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return Response({"code": 400, "msg": "用户名已被占用"})
            user.username = username
            update_fields.append('username')

        if phone:
            user.phone = phone
            update_fields.append('phone')
        if email is not None:
            user.email = email
            update_fields.append('email')

        if update_fields:
            user.save(update_fields=update_fields)

        serializer = UserSerializer(user)
        return Response({"code": 200, "msg": "更新成功", "data": serializer.data})


class AvatarUploadView(APIView):
    """头像上传接口"""
    authentication_classes = [JWTAuthentication]

    CONTENT_TYPE_EXT = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
    }

    def post(self, request):
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({"code": 400, "msg": "请选择头像文件"})

        if avatar_file.content_type not in self.CONTENT_TYPE_EXT:
            return Response({"code": 400, "msg": "仅支持 JPG、PNG、GIF 格式"})

        max_size = 2 * 1024 * 1024
        if avatar_file.size > max_size:
            return Response({"code": 400, "msg": "头像文件大小不能超过 2MB"})

        ext = self.CONTENT_TYPE_EXT[avatar_file.content_type]
        filename = f"{request.user.id}_avatar{ext}"
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, filename)

        try:
            with open(avatar_path, 'wb') as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)
        except OSError:
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
            return Response({"code": 500, "msg": "头像保存失败，请重试"})

        avatar_url = f"{settings.MEDIA_URL}avatars/{filename}"
        request.user.avatar = avatar_url
        request.user.save(update_fields=['avatar'])

        return Response({
            "code": 200,
            "msg": "头像上传成功",
            "data": {"avatar": avatar_url}
        })


class PasswordView(APIView):
    """修改密码接口"""
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"code": 400, "msg": "旧密码和新密码不能为空"})

        if not check_password(old_password, user.password):
            return Response({"code": 400, "msg": "旧密码错误"})

        user.password = make_password(new_password)
        user.save(update_fields=['password'])
        return Response({"code": 200, "msg": "密码修改成功", "data": None})


class ResetPasswordView(APIView):
    """忘记密码 - 通过用户名和手机号重置密码"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        phone = request.data.get('phone')
        captcha = request.data.get('captcha')
        captcha_token = request.data.get('captcha_token')
        new_password = request.data.get('new_password')

        if not all([username, phone, new_password]):
            return Response({"code": 400, "msg": "用户名、手机号和新密码不能为空"})

        if not _check_captcha(captcha_token, captcha, delete_after_verify=True):
            return Response({"code": 400, "msg": "图形验证码错误或已过期"})

        user = User.objects.filter(username=username, phone=phone).first()
        if not user:
            return Response({"code": 404, "msg": "用户信息验证失败"})

        if user.is_active == 0:
            return Response({"code": 403, "msg": "账号已被禁用，请联系管理员"})

        if len(new_password) < 8:
            return Response({"code": 400, "msg": "新密码长度至少为8位"})

        user.password = make_password(new_password)
        user.save(update_fields=['password'])
        return Response({"code": 200, "msg": "密码重置成功，请使用新密码登录", "data": None})


class AdminUserListView(APIView):
    """管理员：用户列表"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        keyword = request.query_params.get('keyword', '')

        queryset = User.objects.all().order_by('-create_time')
        if keyword:
            queryset = queryset.filter(username__icontains=keyword)

        total = queryset.count()
        start = (page - 1) * page_size
        users = queryset[start:start + page_size]
        serializer = UserSerializer(users, many=True)
        return Response({
            "code": 200,
            "msg": "查询成功",
            "data": {
                "total": total,
                "list": serializer.data,
                "page": page,
                "page_size": page_size,
            }
        })


class AdminUserDetailView(APIView):
    """管理员：编辑/删除用户"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        user = User.objects.filter(id=pk).first()
        if not user:
            return Response({"code": 404, "msg": "用户不存在"})

        is_active = request.data.get('is_active')
        is_admin = request.data.get('is_admin')
        if is_active is not None:
            user.is_active = int(is_active)
        if is_admin is not None:
            user.is_admin = int(is_admin)
        user.save(update_fields=['is_active', 'is_admin'])
        serializer = UserSerializer(user)
        return Response({"code": 200, "msg": "更新成功", "data": serializer.data})

    def delete(self, request, pk):
        if str(request.user.id) == str(pk):
            return Response({"code": 400, "msg": "不能删除自己"})
        User.objects.filter(id=pk).delete()
        return Response({"code": 200, "msg": "删除成功", "data": None})
