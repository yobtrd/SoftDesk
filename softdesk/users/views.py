from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from users.models import User
from users.permissions import IsSelf
from users.serializers import (
    UserBaseSerializer,
    UserListSerializer,
)


class UsersViewset(ModelViewSet):
    """Viewset for user's account, with specific permissions."""

    serializer_class = UserBaseSerializer
    model = User
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Select serializer based on current action."""

        if self.action == 'list':
            return UserListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """Dynamically assign permissions based on view action."""

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
