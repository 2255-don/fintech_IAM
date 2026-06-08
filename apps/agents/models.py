from django.db import models

from apps.core.models import AuditModel


class Agent(AuditModel):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="agent_profile",
    )
    code = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "agent"
        verbose_name_plural = "agents"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.user.get_display_name()}"
