from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from apps.subscriptions.services import user_has_premium


class IsPremiumUser(permissions.BasePermission):
    message = "Premium subscription required."

    def has_permission(self, request, view) -> bool:
        if user_has_premium(request.user):
            return True
        raise PermissionDenied(self.message)
