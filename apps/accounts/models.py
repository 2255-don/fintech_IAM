from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrateur"
    AGENT = "AGENT", "Agent"


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ADMIN,
    )

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    @property
    def is_admin_role(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def is_agent_role(self) -> bool:
        return self.role == UserRole.AGENT

    def get_display_name(self) -> str:
        full_name = self.get_full_name().strip()
        return full_name or self.username
