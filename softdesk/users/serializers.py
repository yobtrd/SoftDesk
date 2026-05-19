from rest_framework.serializers import ModelSerializer, ValidationError
from users.models import User
from users.utils import current_year


class UserBaseSerializer(ModelSerializer):
    """Base serializer for User model with full field handling.

    Provides validation, creation and password handling for User instances.
    """

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'year_of_birth',
            'can_be_contacted',
            'can_data_be_shared',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_year_of_birth(self, value):
        """Verifies the user's age, except for administrators."""

        if value is None:
            if not self.context['request'].user.is_superuser:
                raise ValidationError({"year_of_birth": "Champ obligatoire"})
            return None

        if current_year() - value < 15:
            raise ValidationError(
                {
                    "year_of_birth": "Seul les utilisateurs de plus de 15 ans "
                    "peuvent créer un compte."
                },
                code='underage',
            )
        return value

    def create(self, validated_data):
        """Create user with hashed password and optional fields."""

        user = User(
            username=validated_data['username'],
            year_of_birth=validated_data['year_of_birth'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserListSerializer(ModelSerializer):
    """Minimal serializer for User listing operations."""

    class Meta:
        model = User
        fields = ['id', 'username']
