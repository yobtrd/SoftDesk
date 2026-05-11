from issues.fields import AssignmentUsernameField, ProjectNameField, UsernameField
from issues.models import Comment, Contributor, Issue, Project, User
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
)


class ContributorSerializer(ModelSerializer):

    user = UsernameField()
    project = ProjectNameField()

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']

    def validate_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError(f"Il n'existe aucun utilisateur {username}")

    def validate_project(self, name):
        try:
            return Project.objects.get(name=name)
        except Project.DoesNotExist:
            raise ValidationError(f"Il n'existe aucun projet intitulé {name}")

    def validate(self, data):
        user = data['user']
        project = data['project']
        if Contributor.objects.filter(user=user, project=project).exists():
            raise ValidationError({"user": f"{user} est déjà contributeur du projet."})
        return data

    def create(self, validated_data):
        return Contributor.objects.create(
            user=validated_data['user'], project=validated_data['project']
        )


class ProjectSerializer(ModelSerializer):

    author = CharField(source='author.username', read_only=True)
    contributor = ContributorSerializer(
        source='contributors', many=True, read_only=True
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'author', 'contributor', 'description', 'type']

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(author=user, **validated_data)
        Contributor.objects.get_or_create(user=user, project=project)
        project.save()
        return project


class IssueSerializer(ModelSerializer):

    project = ProjectNameField()
    author = CharField(source='author.user.username', read_only=True)
    assignment = AssignmentUsernameField(required=False)

    class Meta:
        model = Issue
        fields = [
            'id',
            'project',
            'name',
            'author',
            'assignment',
            'created_time',
            'description',
            'statut',
            'priority',
            'tag',
        ]

    def validate_project(self, name):
        try:
            return Project.objects.get(name=name)
        except Project.DoesNotExist:
            raise ValidationError(f"Il n'existe aucun projet intitulé {name}")

    def validate(self, data):
        project = data['project']
        assigned = data.get('assignment')

        if assigned:
            if not project.contributors.filter(user__username=assigned).exists():
                raise ValidationError(
                    {
                        "assignment": f"Il n'existe aucun contributeur nommé {assigned}"
                        " dans ce projet."
                    }
                )
            data['assignment'] = project.contributors.get(user__username=assigned)

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        project = validated_data['project']
        print("ca va planter")
        author = Contributor.objects.get(user=user, project=project)
        print("tu ne verras pas ce message")

        if not validated_data.get('assignment'):
            validated_data['assignment'] = author

        return Issue.objects.create(author=author, **validated_data)


class CommentSerializer(ModelSerializer):

    issue = PrimaryKeyRelatedField(queryset=Issue.objects.all())
    author = CharField(source='author.user.username', read_only=True)
    uuid = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['issue', 'uuid', 'author', 'created_time', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        issue = validated_data['issue']
        author = Contributor.objects.get(user=user, project=issue.project)
        return Comment.objects.create(author=author, **validated_data)
