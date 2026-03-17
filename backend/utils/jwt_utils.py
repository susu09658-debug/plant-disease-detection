import jwt
import datetime
from django.conf import settings


def generate_token(user_id, username, is_admin):
    """生成 JWT Token，有效期7天"""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_EXPIRY_DAYS),
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    return token


def parse_token(token):
    """解析 JWT Token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
