from issues.models import Comment, Contributor, Issue, Project
from issues.serializers import (
    CommentSerializer,
    ContributorSerializer,
    IssueSerializer,
    ProjectSerializer,
)

from rest_framework.viewsets import ModelViewSet


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    model = Contributor
    queryset = Contributor.objects.all()


class ProjectViewset(ModelViewSet):

    serializer_class = ProjectSerializer
    model = Project
    queryset = Project.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}


class IssueViewset(ModelViewSet):

    serializer_class = IssueSerializer
    model = Issue
    queryset = Issue.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}


class CommentViewset(ModelViewSet):

    serializer_class = CommentSerializer
    model = Comment
    queryset = Comment.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}
