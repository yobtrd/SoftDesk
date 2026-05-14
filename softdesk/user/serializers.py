from rest_framework.serializers import ModelSerializer, ValidationError
from user.models import User
from user.utils import current_year


class UserCreationSerializer(ModelSerializer):
    """Serializer user with all model's fields and hashed password."""

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
        """Check the year of birth, except for administrators."""
        if value is None:
            if not self.context['request'].user.is_superuser:
                raise ValidationError({"year_of_birth": "Champ obligatoire"})
            return None

        if current_year() - value < 15:
            raise ValidationError(
                {"year_of_birth": "15 ans minimum requis."}, code='underage'
            )
        return value

    def create(self, validated_data):
        """Create a user with hashed password."""
        user = User(
            username=validated_data['username'],
            year_of_birth=validated_data['year_of_birth'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserListSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class UserDetailSerializer(UserListSerializer):
    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + [
            'year_of_birth',
            'can_be_contacted',
            'can_data_be_shared',
        ]
