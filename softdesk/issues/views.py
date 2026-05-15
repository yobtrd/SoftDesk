from rest_framework.permissions import IsAuthenticated, OR
from issues.permissions import IsAuthor, IsContributor, IsProjectAuthor, IsSelf
from issues.models import Comment, Contributor, Issue, Project
from issues.serializers import (
    ContributorSerializer,
    IssueCreateSerializer,
    IssueListSerializer,
    IssueDetailSerializer,
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    CommentSerializer,
    CommentListSerializer,
)

from rest_framework.viewsets import ModelViewSet


class MultipleSerializerMixin:
    """Dynamically switches serializers based on action type."""

    create_serializer_class = None
    list_serializer_class = None
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return self.create_serializer_class
        elif self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class


class BasePermissionViewset(ModelViewSet):
    """Adds basic permissions for all resources.

    - Only authenticated users can access the resources.
    - Only ressource's author can edit or delete it.
    """

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthor()]
        return [IsAuthenticated()]


class ProjectViewset(MultipleSerializerMixin, BasePermissionViewset, ModelViewSet):
    """Handles project lifecycle with dynamic serialization and secure access control.

    Inherits MultipleSerializerMixin to use distinct serializers for different action.

    Queryset automatically filters to projects where requesting user is contributor,
    with optimized prefetching of related contributors and issues for performance.
    """

    create_serializer_class = ProjectCreateSerializer
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    model = Project

    def get_queryset(self):
        """Returns projects where user is contributor through proper M2M traversal.
        Prefetch contributors and issues to prevent n+1 query.
        """

        return Project.objects.filter(
            contributors__user=self.request.user
        ).prefetch_related('contributors', 'issues')


class ContributorViewset(ModelViewSet):
    """Manages contributors within specific projects with granular permission control.

    Queryset automatically scoped to contributors of specified project via project_pk,
    ensuring data isolation between projects.
    """

    serializer_class = ContributorSerializer
    model = Contributor

    def get_queryset(self):
        """Retrieves only the project contributors via project_pk"""
        return Contributor.objects.filter(project_id=self.kwargs['project_pk'])

    def get_permissions(self):
        """Add specific permissions for contributor.

        - Only project author can add a contributor.
        - Only project contributor can list or detail.
        - Only an authenticated user or the project owner can delete
        his contributor's profile.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsProjectAuthor()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), OR(IsProjectAuthor(), IsSelf())]
        return [IsAuthenticated(), IsContributor()]


class IssueViewset(MultipleSerializerMixin, BasePermissionViewset, ModelViewSet):
    """Handles issue lifecycle within specific projects using dynamic serialization.

    Inherits:
    - MultipleSerializerMixin for action-specific serializers
    - BasePermissionViewset for core author/edit permissions

    Queryset automatically scoped to issues of parent project via project_pk.

    Apply specific permissions to child resources for secure access.
    """

    create_serializer_class = IssueCreateSerializer
    list_serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    model = Issue

    def get_queryset(self):
        """Retrieves only the project issues via project_pk.
        Prefetch comments to prevent n+1 query."""

        return Issue.objects.filter(
            project_id=self.kwargs['project_pk']
        ).prefetch_related('comments')

    def get_permissions(self):
        """Ensures that only project contributors have access to the resource."""

        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), IsContributor()]
        return super().get_permissions()


class CommentViewset(BasePermissionViewset, ModelViewSet):
    """Handles comment lifecycle within specific issue using dynamic serialization,
    use UUID as endpoint reference.

    Inherits BasePermissionViewset for core author/edit permissions

    Queryset automatically scoped to comment of parent issue and project
    via project_pk and issue_pk.

    Apply specific permissions to child resources for secure access.
    """

    serializer_class = CommentSerializer
    list_serializer_class = CommentListSerializer

    model = Comment
    lookup_field = 'uuid'

    def get_queryset(self):
        """Retrieves only the issue comments via issue_pk and project_pk"""
        return Comment.objects.filter(
            issue__pk=self.kwargs['issue_pk'],
            issue__project_id=self.kwargs['project_pk'],
        )

    def get_serializer_class(self):
        """Use a lighter serialization format for lists."""
        if self.action == 'list':
            return self.list_serializer_class
        return self.serializer_class

    def get_permissions(self):
        """Ensures that only project contributors have access to the resource."""
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), IsContributor()]
        return super().get_permissions()
