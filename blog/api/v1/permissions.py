from rest_framework import exceptions, permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Доступ к изменеию поста разрешен автору или администратору,
    остальные пользователи чтение, или добавление поста для зарегистрированных.
    """

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            raise exceptions.PermissionDenied(
                "Доступ запрещен. Вам необходимо авторизоваться для выполнения этого действия.")
        return True

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.auth_user == request.user or request.user.is_staff
