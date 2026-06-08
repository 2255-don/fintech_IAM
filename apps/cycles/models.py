from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import AuditModel


class CycleStatus(models.TextChoices):
    EN_COURS = "EN_COURS", "En cours"
    CLOTURE = "CLOTURE", "Cloture"
    CLOTURE_ANTICIPEE = "CLOTURE_ANTICIPEE", "Cloture anticipee"


class Cycle(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="cycles",
    )
    mise = models.PositiveIntegerField()
    nb_collectes = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(31)],
    )
    statut = models.CharField(
        max_length=30,
        choices=CycleStatus.choices,
        default=CycleStatus.EN_COURS,
    )
    date_ouverture = models.DateTimeField(default=timezone.now)
    date_fermeture = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "cycle"
        verbose_name_plural = "cycles"
        ordering = ["-date_ouverture", "code"]
        constraints = [
            models.CheckConstraint(
                condition=Q(mise__gt=0),
                name="cycle_mise_gt_0",
            ),
            models.CheckConstraint(
                condition=Q(nb_collectes__gte=0) & Q(nb_collectes__lte=31),
                name="cycle_nb_collectes_between_0_31",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.client.code}"
