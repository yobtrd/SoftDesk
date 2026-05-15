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
        return super().get_serializer_class()


class BasePermissionViewset(ModelViewSet):

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthor()]
        return [IsAuthenticated()]


class ProjectViewset(MultipleSerializerMixin, BasePermissionViewset, ModelViewSet):

    create_serializer_class = ProjectCreateSerializer
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    model = Project

    def get_queryset(self):
        return Project.objects.filter(
            contributors__user=self.request.user
        ).prefetch_related('contributors', 'issues')


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    model = Contributor

    def get_queryset(self):
        return Contributor.objects.filter(project_id=self.kwargs['project_pk'])

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated(), IsProjectAuthor()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), OR(IsProjectAuthor(), IsSelf())]
        return [IsAuthenticated(), IsContributor()]


class IssueViewset(MultipleSerializerMixin, BasePermissionViewset, ModelViewSet):

    create_serializer_class = IssueCreateSerializer
    list_serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    model = Issue

    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs['project_pk']
        ).prefetch_related('comments')

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), IsContributor()]
        return super().get_permissions()


class CommentViewset(BasePermissionViewset, ModelViewSet):

    serializer_class = CommentSerializer
    list_serializer_class = CommentListSerializer

    model = Comment
    lookup_field = 'uuid'

    def get_queryset(self):
        return Comment.objects.filter(
            issue__pk=self.kwargs['issue_pk'],
            issue__project_id=self.kwargs['project_pk'],
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), IsContributor()]
        return super().get_permissions()
