from django.db import transaction

from apps.core.exceptions import (
    CollecteLimitExceededError,
    CycleClosedError,
    InvalidNbMisesError,
)
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.calculations import calculate_montant_depot
from apps.transactions.models import Depot, Mouvement, MouvementSens, MouvementType

from .close_cycle_service import CloseCycleService


class DepotService:
    @staticmethod
    def validate_nb_mises(nb_mises: int) -> None:
        if nb_mises <= 0:
            raise InvalidNbMisesError("Le nombre de mises doit etre strictement positif.")

    @classmethod
    @transaction.atomic
    def create_depot(cls, *, code: str, cycle_id: int, nb_mises: int, created_by=None) -> Depot:
        cls.validate_nb_mises(nb_mises)

        cycle = Cycle.objects.select_for_update().select_related("client__agent").get(id=cycle_id)

        if cycle.statut in {CycleStatus.CLOTURE, CycleStatus.CLOTURE_ANTICIPEE}:
            raise CycleClosedError("Impossible d'ajouter un depot sur un cycle cloture.")

        next_collectes = cycle.nb_collectes + nb_mises
        if next_collectes > 31:
            raise CollecteLimitExceededError("Le cycle ne peut jamais depasser 31 collectes.")

        montant = calculate_montant_depot(mise=cycle.mise, nb_mises=nb_mises)
        depot = Depot.objects.create(
            code=code,
            cycle=cycle,
            client=cycle.client,
            agent=cycle.client.agent,
            nb_mises=nb_mises,
            montant=montant,
            created_by=created_by,
            updated_by=created_by,
        )

        Mouvement.objects.create(
            code=f"MVT-{depot.code}",
            client=cycle.client,
            cycle=cycle,
            agent=cycle.client.agent,
            type=MouvementType.MISE,
            sens=MouvementSens.ENTREE,
            montant=montant,
            description="Depot enregistre sur le cycle.",
            reference_operation=depot.code,
            created_by=created_by,
            updated_by=created_by,
        )

        cycle.nb_collectes = next_collectes
        cycle.updated_by = created_by
        cycle.save(update_fields=["nb_collectes", "updated_by", "updated_at"])

        if cycle.nb_collectes == 31:
            CloseCycleService.close_cycle(cycle=cycle, created_by=created_by)

        return depot
