from django.test import TestCase

from apps.transactions.calculations import (
    calculate_close_cycle_distribution,
    calculate_emergency_withdrawal_distribution,
    calculate_montant_depot,
)


class TransactionCalculationTests(TestCase):
    def test_calculate_montant_depot_returns_expected_value(self):
        self.assertEqual(calculate_montant_depot(mise=1000, nb_mises=5), 5000)

    def test_calculate_close_cycle_distribution_returns_expected_values(self):
        calculation = calculate_close_cycle_distribution(mise=1000, nb_collectes=31)

        self.assertEqual(calculation.total_collecte, 31000)
        self.assertEqual(calculation.retenue, 1000)
        self.assertEqual(calculation.commission_agent, 500)
        self.assertEqual(calculation.commission_institution, 500)
        self.assertEqual(calculation.credit_client, 30000)

    def test_calculate_emergency_withdrawal_distribution_returns_expected_values(self):
        calculation = calculate_emergency_withdrawal_distribution(mise=1000, nb_collectes=20, montant=10000)

        self.assertEqual(calculation.total_collecte, 20000)
        self.assertEqual(calculation.penalite, 1000)
        self.assertEqual(calculation.commission_agent, 500)
        self.assertEqual(calculation.commission_institution, 500)
        self.assertEqual(calculation.montant_maximal, 19000)
        self.assertEqual(calculation.montant_restant_en_credit, 9000)
        self.assertEqual(calculation.montant_net_client, 10000)
