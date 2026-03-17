import base64
import hashlib
import io
import random
import string

from PIL import Image, ImageDraw, ImageFont
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

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


class SmsCodeView(APIView):
    """短信验证码占位接口（用于打通前端流程）"""

    def post(self, request):
        phone = request.data.get("phone")
        captcha = request.data.get("captcha")
        captcha_token = request.data.get("captcha_token")

        if not phone:
            return Response({"code": 400, "msg": "手机号不能为空", "data": None})

        if not _check_captcha(captcha_token, captcha):
            return Response({"code": 400, "msg": "图形验证码错误或已过期", "data": None})

        return Response({"code": 200, "msg": "短信验证码已发送(演示模式)", "data": None})


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
        captcha = request.data.get('captcha')
        captcha_token = request.data.get('captcha_token')

        if not username or not password:
            return Response({"code": 400, "msg": "用户名或密码不能为空"})

        if not _check_captcha(captcha_token, captcha, delete_after_verify=True):
            return Response({"code": 400, "msg": "图形验证码错误或已过期"})

        # 将前端传来的明文密码进行同样的 MD5 加密，再与数据库比对
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        hashed_password = md5.hexdigest()

        # 查询数据库比对账号密码
        user = User.objects.filter(username=username, password=hashed_password).first()

        if user:
            # 登录成功，返回用户信息及一个简易的身份凭证(Token)
            serializer = UserSerializer(user)
            return Response(
                {
                    "code": 200,
                    "msg": "登录成功",
                    "data": {
                        "token": f"user_token_{user.id}",
                        "user_info": serializer.data,
                    },
                }
            )

        return Response({"code": 401, "msg": "用户名或密码错误"})