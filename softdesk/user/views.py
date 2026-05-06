from rest_framework.permissions import OR, IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from user.models import User
from user.permissions import IsSelf
from user.serializers import UserSerializer


class UsersViewset(ModelViewSet):
    """Viewset for user's account, with specific permissions."""

    serializer_class = UserSerializer
    model = User

    def get_queryset(self):
        """Applies the principle of least privilege."""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        """Manage permissions for each action."""
        permissions = {
            'create': [],
            'list': [IsAuthenticated(), IsAdminUser()],
            'retrieve': [IsAuthenticated(), OR(IsSelf(), IsAdminUser())],
            'update': [IsAuthenticated(), IsSelf()],
            'partial_update': [IsAuthenticated(), IsSelf()],
            'destroy': [IsAuthenticated(), OR(IsSelf(), IsAdminUser())],
        }
        return permissions.get(self.action)
