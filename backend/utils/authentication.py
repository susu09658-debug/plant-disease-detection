from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.user.models import User
from utils.jwt_utils import parse_token


class JWTAuthentication(BaseAuthentication):
    """自定义 JWT 认证类"""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()
        payload = parse_token(token)
        if payload is None:
            raise AuthenticationFailed('Token 无效或已过期')

        user_id = payload.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('用户不存在')

        if user.is_active == 0:
            raise AuthenticationFailed('账号已被禁用')

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
