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
        if self.action in ['create', 'update', 'partial']:
            return self.create_serializer_class
        elif self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class


class ProjectViewset(MultipleSerializerMixin, ModelViewSet):

    create_serializer_class = ProjectCreateSerializer
    list_serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    model = Project
    queryset = Project.objects.all().prefetch_related('contributors', 'issues')


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    model = Contributor

    def get_queryset(self):
        return Contributor.objects.filter(project_id=self.kwargs['project_pk'])


class IssueViewset(MultipleSerializerMixin, ModelViewSet):

    create_serializer_class = IssueCreateSerializer
    list_serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    model = Issue

    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs['project_pk']
        ).prefetch_related('comments')


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    list_serializer_class = CommentListSerializer

    model = Comment
    lookup_field = 'uuid'

    def get_queryset(self):
        return Comment.objects.filter(issue=self.kwargs['issue_pk'])

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return self.serializer_class
