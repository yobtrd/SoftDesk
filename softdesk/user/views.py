from rest_framework.permissions import IsAuthenticated
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
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreationSerializer
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        elif self.action == "list":
            return [IsAuthenticated()]
        elif self.action in [
            'retrieve',
            'update',
            'partial_update',
            'destroy',
        ]:
            return [IsAuthenticated(), IsSelf()]
