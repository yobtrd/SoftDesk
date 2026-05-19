from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):
    """Allowsa access only to authenticated users as current user."""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
