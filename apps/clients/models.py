from django.db import models

from apps.core.models import AuditModel


class Client(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.PROTECT,
        related_name="clients",
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"
        ordering = ["nom", "prenom", "code"]

    def __str__(self) -> str:
        full_name = f"{self.nom} {self.prenom}".strip()
        return f"{self.code} - {full_name}"
