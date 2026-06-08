from dataclasses import dataclass

from django.utils import timezone

from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.calculations import calculate_close_cycle_distribution
from apps.transactions.models import Mouvement, MouvementSens, MouvementType, Retenue


@dataclass
class CloseCycleResult:
    cycle: Cycle
    retenue: Retenue
    credit_client: int
    commission_agent: int
    commission_institution: int


class CloseCycleService:
    @staticmethod
    def build_code(prefix: str, cycle: Cycle) -> str:
        return f"{prefix}-{cycle.code}"

    @classmethod
    def close_cycle(cls, *, cycle: Cycle, created_by=None) -> CloseCycleResult:
        calculation = calculate_close_cycle_distribution(
            mise=cycle.mise,
            nb_collectes=cycle.nb_collectes,
        )

        retenue = Retenue.objects.create(
            code=cls.build_code("RET", cycle),
            cycle=cycle,
            client=cycle.client,
            agent=cycle.client.agent,
            montant=calculation.retenue,
            commission_agent=calculation.commission_agent,
            commission_institution=calculation.commission_institution,
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
        Mouvement.objects.bulk_create(
            [
                Mouvement(
                    code=cls.build_code("MVT-RET", cycle),
                    type=MouvementType.RETENUE,
                    sens=MouvementSens.SORTIE,
                    montant=calculation.retenue,
                    description="Retenue de cloture du cycle.",
                    reference_operation=retenue.code,
                    **common_kwargs,
                ),
                Mouvement(
                    code=cls.build_code("MVT-AGT", cycle),
                    type=MouvementType.COM_AGENT,
                    sens=MouvementSens.ENTREE,
                    montant=calculation.commission_agent,
                    description="Commission agent sur cloture de cycle.",
                    reference_operation=retenue.code,
                    **common_kwargs,
                ),
                Mouvement(
                    code=cls.build_code("MVT-INS", cycle),
                    type=MouvementType.COM_INSTITUTION,
                    sens=MouvementSens.ENTREE,
                    montant=calculation.commission_institution,
                    description="Commission institution sur cloture de cycle.",
                    reference_operation=retenue.code,
                    **common_kwargs,
                ),
                Mouvement(
                    code=cls.build_code("MVT-CRD", cycle),
                    type=MouvementType.CREDIT_CLIENT,
                    sens=MouvementSens.ENTREE,
                    montant=calculation.credit_client,
                    description="Credit client apres cloture du cycle.",
                    reference_operation=retenue.code,
                    **common_kwargs,
                ),
            ]
        )

        cycle.statut = CycleStatus.CLOTURE
        cycle.date_fermeture = timezone.now()
        cycle.updated_by = created_by
        cycle.save(update_fields=["statut", "date_fermeture", "updated_by", "updated_at"])

        return CloseCycleResult(
            cycle=cycle,
            retenue=retenue,
            credit_client=calculation.credit_client,
            commission_agent=calculation.commission_agent,
            commission_institution=calculation.commission_institution,
        )
