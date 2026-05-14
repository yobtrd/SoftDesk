from rest_framework.permissions import OR, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from user.models import User
from user.permissions import IsSelf
from user.serializers import (
    UserCreationSerializer,
    UserListSerializer,
    UserDetailSerializer,
)


class UsersViewset(ModelViewSet):
    """Viewset for user's account, with specific permissions."""

    model = User

    def get_queryset(self):
        """Applies the principle of least privilege."""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreationSerializer
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer

    def get_permissions(self):
        """Manage permissions for each action."""
        permissions = {
            'create': [],
            'list': [IsAuthenticated()],
            'retrieve': [IsAuthenticated(), OR(IsSelf(), IsAdminUser())],
            'update': [IsAuthenticated(), IsSelf()],
            'partial_update': [IsAuthenticated(), IsSelf()],
            'destroy': [IsAuthenticated(), OR(IsSelf(), IsAdminUser())],
        }
        return permissions.get(self.action)
