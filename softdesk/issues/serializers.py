from issues.models import Comment, Contributor, Issue, Project, User
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
    SerializerMethodField,
)


class ContributorSerializer(ModelSerializer):

    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'username']

    def validate(self, data):
        project = Project.objects.get(pk=self.context['view'].kwargs['project_pk'])
        data['project'] = project

        if Contributor.objects.filter(user=data['user'], project=project).exists():
            raise ValidationError(
                {"user": f"{data['user'].username} est déjà contributeur du projet."}
            )

        return data

    def create(self, validated_data):
        return Contributor.objects.create(**validated_data)


class ProjectCreateSerializer(ModelSerializer):

    author = CharField(source='author.username', read_only=True)
    contributor = ContributorSerializer(
        source='contributors', many=True, read_only=True
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'author',
            'contributor',
            'description',
            'type',
            'created_time',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(author=user, **validated_data)
        Contributor.objects.get_or_create(user=user, project=project)
        return project


class ProjectListSerializer(ModelSerializer):

    author = CharField(source='author.username', read_only=True)
    issue_count = SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'author',
            'type',
            'issue_count',
        ]

    def get_issue_count(self, obj):
        return len(obj.issues.all())


class ProjectDetailSerializer(ModelSerializer):

    author = CharField(source='author.username', read_only=True)
    contributor_count = SerializerMethodField()
    issue_count = SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'author',
            'contributor_count',
            'description',
            'created_time',
            'type',
            'issue_count',
        ]

    def get_contributor_count(self, obj):
        return len(obj.contributors.all())

    def get_issue_count(self, obj):
        return len(obj.issues.all())


class IssueCreateSerializer(ModelSerializer):

    author = CharField(source='author.user.username', read_only=True)
    assignment = PrimaryKeyRelatedField(
        queryset=Contributor.objects.all(), required=False, allow_null=True
    )
    assignment_username = CharField(source='assignment.user.username', read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'name',
            'author',
            'assignment',
            'assignment_username',
            'created_time',
            'description',
            'statut',
            'priority',
            'tag',
        ]

    def validate(self, data):
        project = Project.objects.get(pk=self.context['view'].kwargs['project_pk'])
        data['project'] = project

        if 'assignment' in data:
            assignment = data['assignment']
            if (
                assignment
                and not project.contributors.filter(pk=assignment.pk).exists()
            ):
                raise ValidationError(
                    {
                        "assignment": f"L'user nommé {assignment.user.username} "
                        "n'est pas contributeur de ce projet."
                    }
                )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author = Contributor.objects.get(user=user, project=validated_data['project'])

        if 'assignment' not in validated_data or validated_data['assignment'] is None:
            validated_data['assignment'] = author

        return Issue.objects.create(author=author, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('assigment') is None:
            validated_data['assignment'] = instance.author
        return super().update(instance, validated_data)


class IssueListSerializer(ModelSerializer):

    author = CharField(source='author.user.username', read_only=True)
    assignment = CharField(source='assignment.user.username', read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'name',
            'author',
            'assignment',
            'statut',
        ]


class IssueDetailSerializer(ModelSerializer):

    author = CharField(source='author.user.username', read_only=True)
    assignment = CharField(source='assignment.user.username', read_only=True)
    comment_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id',
            'name',
            'author',
            'assignment',
            'description',
            'created_time',
            'statut',
            'priority',
            'tag',
            'comment_count',
        ]

    def get_comment_count(self, obj):
        return len(obj.comments.all())


class CommentSerializer(ModelSerializer):

    author = CharField(source='author.user.username', read_only=True)
    uuid = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'created_time', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        issue = Issue.objects.get(pk=self.context['view'].kwargs['issue_pk'])
        author = Contributor.objects.get(user=user, project=issue.project)
        return Comment.objects.create(author=author, issue=issue, **validated_data)


class CommentListSerializer(ModelSerializer):

    uuid = PrimaryKeyRelatedField(read_only=True)
    author = CharField(source='author.user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'description']
