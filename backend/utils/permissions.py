from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """仅允许管理员访问"""

    def has_permission(self, request, view):
        return bool(
            request.user and
            not isinstance(request.user, type(None)) and
            hasattr(request.user, 'is_admin') and
            request.user.is_admin == 1
        )


class IsActiveUser(BasePermission):
    """仅允许已启用的用户访问"""

    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'is_active') and
            request.user.is_active == 1
        )
