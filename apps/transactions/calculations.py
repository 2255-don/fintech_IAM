from dataclasses import dataclass


@dataclass(frozen=True)
class CloseCycleCalculation:
    total_collecte: int
    retenue: int
    commission_agent: int
    commission_institution: int
    credit_client: int


@dataclass(frozen=True)
class EmergencyWithdrawalCalculation:
    total_collecte: int
    penalite: int
    commission_agent: int
    commission_institution: int
    montant_maximal: int
    montant_restant_en_credit: int
    montant_net_client: int


def calculate_montant_depot(*, mise: int, nb_mises: int) -> int:
    return mise * nb_mises


def calculate_close_cycle_distribution(*, mise: int, nb_collectes: int) -> CloseCycleCalculation:
    total_collecte = mise * nb_collectes
    retenue = mise
    commission_agent = retenue // 2
    commission_institution = retenue - commission_agent
    credit_client = total_collecte - retenue

    return CloseCycleCalculation(
        total_collecte=total_collecte,
        retenue=retenue,
        commission_agent=commission_agent,
        commission_institution=commission_institution,
        credit_client=credit_client,
    )


def calculate_emergency_withdrawal_distribution(*, mise: int, nb_collectes: int, montant: int) -> EmergencyWithdrawalCalculation:
    total_collecte = mise * nb_collectes
    penalite = mise
    montant_maximal = max(total_collecte - penalite, 0)
    commission_agent = penalite // 2
    commission_institution = penalite - commission_agent
    montant_restant_en_credit = max(total_collecte - penalite - montant, 0)

    return EmergencyWithdrawalCalculation(
        total_collecte=total_collecte,
        penalite=penalite,
        commission_agent=commission_agent,
        commission_institution=commission_institution,
        montant_maximal=montant_maximal,
        montant_restant_en_credit=montant_restant_en_credit,
        montant_net_client=montant,
    )
