from rest_framework.permissions import BasePermission
from issues.models import Project
from rest_framework.exceptions import NotFound


class IsContributor(BasePermission):
    message = "Vous devez être contributeur pour créer ou accéder aux ressources."

    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk')

        try:
            Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            raise NotFound(detail="Projet non trouvé.")

        return request.user.contributor_profile.filter(project_id=project_pk).exists()


class IsAuthor(BasePermission):
    message = "Vous devez être l'auteur de cette ressource pour la modifier."

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return obj.author == request.user
        return obj.author.user == request.user


class IsProjectAuthor(BasePermission):
    message = "Seul l'auteur du projet peut ajouter ou modifier les contributeurs."

    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk')
        return Project.objects.filter(pk=project_pk, author=request.user).exists()


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
