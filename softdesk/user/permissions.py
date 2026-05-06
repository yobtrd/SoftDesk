from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """Allows only authenticated users."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
