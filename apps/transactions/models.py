from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.utils import timezone

from apps.core.models import AuditModel


class MouvementType(models.TextChoices):
    MISE = "MISE", "Mise"
    RETENUE = "RETENUE", "Retenue"
    COM_AGENT = "COM_AGENT", "Commission agent"
    COM_INSTITUTION = "COM_INSTITUTION", "Commission institution"
    CREDIT_CLIENT = "CREDIT_CLIENT", "Credit client"
    RETRAIT = "RETRAIT", "Retrait"
    RETRAIT_URGENCE = "RETRAIT_URGENCE", "Retrait urgence"
    PENALITE_URGENCE = "PENALITE_URGENCE", "Penalite urgence"


class MouvementSens(models.TextChoices):
    ENTREE = "ENTREE", "Entree"
    SORTIE = "SORTIE", "Sortie"
    INFO = "INFO", "Information"


class RetraitType(models.TextChoices):
    STANDARD = "STANDARD", "Retrait standard"
    URGENCE = "URGENCE", "Retrait d'urgence"


class Depot(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    cycle = models.ForeignKey(
        "cycles.Cycle",
        on_delete=models.PROTECT,
        related_name="depots",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="depots",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.PROTECT,
        related_name="depots",
    )
    nb_mises = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    montant = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    date_depot = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "depot"
        verbose_name_plural = "depots"
        ordering = ["-date_depot", "code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.montant} FCFA"


class Retenue(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    cycle = models.OneToOneField(
        "cycles.Cycle",
        on_delete=models.PROTECT,
        related_name="retenue",
    )
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="retenues",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        on_delete=models.PROTECT,
        related_name="retenues",
    )
    montant = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    commission_agent = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    commission_institution = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    date_retenue = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "retenue"
        verbose_name_plural = "retenues"
        ordering = ["-date_retenue", "code"]
        constraints = [
            models.CheckConstraint(
                condition=Q(montant__gte=F("commission_agent") + F("commission_institution")),
                name="retenue_commissions_not_exceed_montant",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.montant} FCFA"


class Retrait(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        related_name="retraits",
    )
    cycle = models.ForeignKey(
        "cycles.Cycle",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="retraits",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="retraits",
    )
    type = models.CharField(max_length=20, choices=RetraitType.choices, default=RetraitType.STANDARD)
    montant = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    date_retrait = models.DateTimeField(default=timezone.now)
    motif = models.TextField(blank=True)

    class Meta:
        verbose_name = "retrait"
        verbose_name_plural = "retraits"
        ordering = ["-date_retrait", "code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.montant} FCFA"


class Mouvement(AuditModel):
    code = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "clients.Client",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="mouvements",
    )
    cycle = models.ForeignKey(
        "cycles.Cycle",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="mouvements",
    )
    agent = models.ForeignKey(
        "agents.Agent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mouvements",
    )
    type = models.CharField(max_length=50, choices=MouvementType.choices)
    sens = models.CharField(max_length=20, choices=MouvementSens.choices)
    montant = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    reference_operation = models.CharField(max_length=100, blank=True)
    date_mouvement = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "mouvement"
        verbose_name_plural = "mouvements"
        ordering = ["-date_mouvement", "code"]
        constraints = [
            models.CheckConstraint(
                condition=~(Q(client__isnull=True) & Q(cycle__isnull=True) & Q(agent__isnull=True)),
                name="mouvement_has_at_least_one_relation",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.type}"
