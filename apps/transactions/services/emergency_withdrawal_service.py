from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import (
    EmergencyWithdrawalAmountExceededError,
    EmergencyWithdrawalNotAllowedError,
)
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.calculations import calculate_emergency_withdrawal_distribution
from apps.transactions.models import Mouvement, MouvementSens, MouvementType, Retrait, RetraitType


@dataclass
class EmergencyWithdrawalResult:
    cycle: Cycle
    retrait: Retrait
    penalite: int
    commission_agent: int
    commission_institution: int
    credit_client: int


class EmergencyWithdrawalService:
    @staticmethod
    def build_code(prefix: str, cycle: Cycle) -> str:
        return f"{prefix}-{cycle.code}"

    @classmethod
    @transaction.atomic
    def create_emergency_withdrawal(
        cls,
        *,
        cycle_id: int,
        montant: int,
        motif: str = "",
        created_by=None,
    ) -> EmergencyWithdrawalResult:
        cycle = Cycle.objects.select_for_update().select_related("client__agent").get(id=cycle_id, deleted_at__isnull=True)

        if cycle.statut != CycleStatus.EN_COURS:
            raise EmergencyWithdrawalNotAllowedError(
                "Le retrait d'urgence est reserve aux cycles en cours."
            )

        if cycle.nb_collectes < 2:
            raise EmergencyWithdrawalNotAllowedError(
                "Le retrait d'urgence necessite au moins 2 mises deja collectees."
            )

        calculation = calculate_emergency_withdrawal_distribution(
            mise=cycle.mise,
            nb_collectes=cycle.nb_collectes,
            montant=montant,
        )

        if montant <= 0:
            raise EmergencyWithdrawalAmountExceededError(
                "Le montant du retrait d'urgence doit etre strictement positif."
            )

        if montant > calculation.montant_maximal:
            raise EmergencyWithdrawalAmountExceededError(
                f"Le retrait d'urgence ne peut pas depasser {calculation.montant_maximal} FCFA."
            )

        retrait = Retrait.objects.create(
            code=cls.build_code("RUR", cycle),
            client=cycle.client,
            cycle=cycle,
            agent=cycle.client.agent,
            type=RetraitType.URGENCE,
            montant=montant,
            motif=motif,
            created_by=created_by,
            updated_by=created_by,
        )

        common_kwargs = {
            "client": cycle.client,
            "cycle": cycle,
            "agent": cycle.client.agent,
            "created_by": created_by,
            "updated_by": created_by,
        }
        mouvements = [
            Mouvement(
                code=cls.build_code("MVT-RUR", cycle),
                type=MouvementType.RETRAIT_URGENCE,
                sens=MouvementSens.SORTIE,
                montant=montant,
                description="Retrait d'urgence enregistre avant la fin du cycle.",
                reference_operation=retrait.code,
                **common_kwargs,
            ),
            Mouvement(
                code=cls.build_code("MVT-PUR", cycle),
                type=MouvementType.PENALITE_URGENCE,
                sens=MouvementSens.SORTIE,
                montant=calculation.penalite,
                description="Penalite appliquee sur retrait d'urgence.",
                reference_operation=retrait.code,
                **common_kwargs,
            ),
            Mouvement(
                code=cls.build_code("MVT-RAG", cycle),
                type=MouvementType.COM_AGENT,
                sens=MouvementSens.ENTREE,
                montant=calculation.commission_agent,
                description="Commission agent issue du retrait d'urgence.",
                reference_operation=retrait.code,
                **common_kwargs,
            ),
            Mouvement(
                code=cls.build_code("MVT-RIN", cycle),
                type=MouvementType.COM_INSTITUTION,
                sens=MouvementSens.ENTREE,
                montant=calculation.commission_institution,
                description="Commission plateforme issue du retrait d'urgence.",
                reference_operation=retrait.code,
                **common_kwargs,
            ),
        ]

        if calculation.montant_restant_en_credit > 0:
            mouvements.append(
                Mouvement(
                    code=cls.build_code("MVT-RCR", cycle),
                    type=MouvementType.CREDIT_CLIENT,
                    sens=MouvementSens.ENTREE,
                    montant=calculation.montant_restant_en_credit,
                    description="Reliquat credite au client apres retrait d'urgence et cloture anticipee.",
                    reference_operation=retrait.code,
                    **common_kwargs,
                )
            )

        Mouvement.objects.bulk_create(mouvements)

        cycle.statut = CycleStatus.CLOTURE_ANTICIPEE
        cycle.date_fermeture = timezone.now()
        cycle.updated_by = created_by
        cycle.save(update_fields=["statut", "date_fermeture", "updated_by", "updated_at"])

        return EmergencyWithdrawalResult(
            cycle=cycle,
            retrait=retrait,
            penalite=calculation.penalite,
            commission_agent=calculation.commission_agent,
            commission_institution=calculation.commission_institution,
            credit_client=calculation.montant_restant_en_credit,
        )
