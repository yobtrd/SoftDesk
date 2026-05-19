from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.utils import current_year


class User(AbstractUser):
    """API's user model based on Auth's core features.

    Extends Django's AbstractUser to add custom fields related to RGPD.

    Attributes:
        year_of_birth (PositiveIntegerField): User's birth year with validation.
        can_be_contacted (BooleanField): Consent for being contacted.
        can_data_be_shared (BooleanField): Consent for data sharing.
    """

    username = models.CharField(
        max_length=150, unique=True, verbose_name="Nom d'utilisateur"
    )
    year_of_birth = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(current_year)],
        null=True,
        verbose_name="Année de naissance",
    )
    can_be_contacted = models.BooleanField(
        default=False, verbose_name="Accepte d'être contacté."
    )
    can_data_be_shared = models.BooleanField(
        default=False, verbose_name="Accepte de partager ses données."
    )
