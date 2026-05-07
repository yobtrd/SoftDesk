from django.db import models
from user.models import User


class Contributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Project(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du projet")
    author = models.ForeignKey(
        'Contributor',
        on_delete=models.PROTECT,
        verbose_name="Auteur du projet",
    )
    contributors = models.ManyToManyField(
        'Contributor',
        related_name='contributed_projects',
        verbose_name="Contributeurs du projet",
    )
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
