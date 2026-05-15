import uuid

from django.db import models
from user.models import User


class Project(models.Model):
    """Software project with contributors, type classification and metadata."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du projet")
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_projects',
        verbose_name="Auteur du projet",
    )
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=1500, verbose_name="Description du projet"
    )
    type = models.CharField(
        max_length=7,
        choices=[
            ('BACK', 'Back-end'),
            ('FRONT', 'Front-end'),
            ('IOS', 'iOS'),
            ('ANDROID', 'Android'),
        ],
        verbose_name="Type de projet",
    )

    def __str__(self):
        return self.name


class Contributor(models.Model):
    """Represents project contributors through a junction table.

    Creates a many-to-many relationship between User and Project
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributor_profile',
        verbose_name="Utilisateur",
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributors"
    )


class Issue(models.Model):
    """Technical issue or task within a Project."""

    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE, related_name='issues'
    )
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Intitulé du problème"
    )
    author = models.ForeignKey(
        'Contributor',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Auteur du problème",
    )
    assignment = models.ForeignKey(
        'Contributor',
        on_delete=models.CASCADE,
        related_name='assigned_contributor',
        verbose_name="Attribution",
    )
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=1500, verbose_name="Description du problème"
    )
    status = models.CharField(
        max_length=11,
        choices=[
            ('TODO', 'To do'),
            ('PROGRESS', 'In progress'),
            ('FINISH', 'Finished'),
        ],
        default='TODO',
        blank=True,
        verbose_name="Statut",
    )
    priority = models.CharField(
        max_length=6,
        choices=[
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
        ],
        verbose_name="Priorité",
    )
    tag = models.CharField(
        max_length=7,
        choices=[('BUG', 'Bug'), ('FEATURE', 'Feature'), ('TASK', 'Task')],
        verbose_name="Balise",
    )


class Comment(models.Model):
    """User comment attached to an Issue, identified by UUID."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    issue = models.ForeignKey(
        'Issue', on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        'Contributor',
        on_delete=models.CASCADE,
        verbose_name="Auteur du commentaire",
    )
    created_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(
        max_length=2000, verbose_name="Contenu du commentaire", blank=False
    )
