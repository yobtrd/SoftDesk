from issues.models import Contributor, Project
from issues.serializers import ContributorSerializer, ProjectSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from user.models import User


class ContributorViewset(ModelViewSet):

    serializer_class = ContributorSerializer
    model = Contributor
    queryset = Contributor.objects.all()


class ProjectViewset(ModelViewSet):

    serializer_class = ProjectSerializer
    model = Project
    queryset = Project.objects.all()

    def perform_create(self, serializer):
        contributor = Contributor.objects.create(user=self.request.user)
        project = serializer.save(author=contributor)
        project.contributors.add(contributor)

    @action(detail=True, methods=['post'])
    def add_contributor(self, request, pk):
        username = request.data.get('username')
        if not username:
            return Response({"error: An username must be entered"}, status=403)
        try:
            user = User.objects.get(username=username)
            contributor, create = Contributor.objects.get_or_create(user=user)
            project = self.get_object()
            if project.contributors.filter(id=contributor.id).exists():
                return Response(
                    {"error": f"{username} is already contributor of the project"},
                    status=403,
                )
            project.contributors.add(contributor)
            return Response({"status": f"{username} added as contributor"})
        except User.DoesNotExist:
            return Response({"error": f"{username} not found."}, status=404)
