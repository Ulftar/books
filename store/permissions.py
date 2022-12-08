from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaffOrReadOnly(BasePermission):
    # Проверяем разрешение на действия над объектом.
    # Удостоверимся, что запрос пришел от пришел от аутентифицированного владельца книги
    # или от авторизованного персонала компании
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            (
                    obj.owner == request.user or
                    request.user.is_staff
            )
        )
