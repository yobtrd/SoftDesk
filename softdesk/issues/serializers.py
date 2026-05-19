from issues.models import Comment, Contributor, Issue, Project
from users.models import User
from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
    SerializerMethodField,
)


class ContributorSerializer(ModelSerializer):
    """Handles validation and contributor assignment with their username display."""

    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    username = CharField(source='user.username', read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'username']

    def validate(self, data):
        """Prevents a user from being added twice as a contributor."""

        project = Project.objects.get(pk=self.context['view'].kwargs['projects_pk'])
        data['project'] = project

        if Contributor.objects.filter(user=data['user'], project=project).exists():
            raise ValidationError(
                {"user": f"{data['user'].username} est déjà contributeur du projet."}
            )
        return data


class ProjectCreateSerializer(ModelSerializer):
    """Handles project creation with automatic contributor assignment.

    Automatically assigns requesting user as both author and first contributor.
    """

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
        """Assigns requesting user as both author and first contributor."""

        user = self.context['request'].user
        project = Project.objects.create(author=user, **validated_data)
        Contributor.objects.create(user=user, project=project)
        return project


class ProjectListSerializer(ModelSerializer):
    """Provides lightweight project listing with essential metadata.

    Exposes minimal project details including prefetched issue count
    for efficient UI display.
    """

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
    """Comprehensive project representation with detailed metrics.

    Exposes full project details including prefetched contributor
    count and issue count.
    """

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
    """Handles issue creation with automatic author assignment and contributor
    validation.

    Validates that assigned contributor belongs to project. Defaults assignment to
    author if unspecified.
    """

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
            'status',
            'priority',
            'tag',
        ]

    def validate(self, data):
        """Verify that the designated contributor is part of the project."""
        project = Project.objects.get(pk=self.context['view'].kwargs['projects_pk'])
        data['project'] = project

        if 'assignment' in data:
            assignment = data['assignment']
            if (
                assignment
                and not project.contributors.filter(pk=assignment.pk).exists()
            ):
                raise ValidationError(
                    {
                        "assignment": "Cet ID ne correspond a aucun contributeur "
                        "du projet."
                    }
                )

        return data

    def create(self, validated_data):
        """Assigns requesting user as both author and assigned contributor
        if no assigment specify.
        """

        user = self.context['request'].user
        author = Contributor.objects.get(user=user, project=validated_data['project'])

        if 'assignment' not in validated_data or validated_data['assignment'] is None:
            validated_data['assignment'] = author

        return Issue.objects.create(author=author, **validated_data)

    def update(self, instance, validated_data):
        """Ensures that the author remains the assigned contributor
        if one is not specified.
        """

        if validated_data.get('assignment') is None:
            validated_data['assignment'] = instance.author
        return super().update(instance, validated_data)


class IssueListSerializer(ModelSerializer):
    """Provides lightweight issue listing with essential metadata."""

    author = CharField(source='author.user.username', read_only=True)
    assignment = CharField(source='assignment.user.username', read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'name',
            'author',
            'assignment',
            'status',
        ]


class IssueDetailSerializer(ModelSerializer):
    """Comprehensive issue representation with detailed metrics.

    Exposes full issue details includind prefetched comments counts.
    """

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
            'status',
            'priority',
            'tag',
            'comment_count',
        ]

    def get_comment_count(self, obj):
        return len(obj.comments.all())


class CommentSerializer(ModelSerializer):
    """Handles comment creation linked to specific issue with author auto-assignment.
    Comprehensive comment representation with detailed metadata.

    Uses UUID for reference.
    """

    author = CharField(source='author.user.username', read_only=True)
    uuid = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'created_time', 'description']

    def create(self, validated_data):
        """Assigns requesting user as author, checks context data before creation."""

        user = self.context['request'].user
        issue = Issue.objects.get(pk=self.context['view'].kwargs['issues_pk'])
        author = Contributor.objects.get(user=user, project=issue.project)
        return Comment.objects.create(author=author, issue=issue, **validated_data)


class CommentListSerializer(ModelSerializer):
    """Provides lightweight comment listing with essential metadata."""

    uuid = PrimaryKeyRelatedField(read_only=True)
    author = CharField(source='author.user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'description']
