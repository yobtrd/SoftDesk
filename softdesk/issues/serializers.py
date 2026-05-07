from issues.models import Contributor, Project
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)


class ContributorSerializer(ModelSerializer):
    username = SerializerMethodField(read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'username']

    def get_username(self, obj):
        return obj.user.username


class ProjectSerializer(ModelSerializer):

    author = PrimaryKeyRelatedField(read_only=True)
    contributors = PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributors', 'description', 'type']
