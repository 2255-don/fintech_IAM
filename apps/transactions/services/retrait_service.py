from django.db import connection, transaction
from django.db.utils import DatabaseError

from apps.clients.models import Client
from apps.core.exceptions import ClientNotFoundError, InsufficientRetirableAmountError
from apps.transactions.models import Retrait

from .reporting_service import ReportingService


class RetraitService:
    @classmethod
    @transaction.atomic
    def create_retrait(
        cls,
        *,
        client_id: int,
        montant: int,
        created_by=None,
        motif: str = "",
    ) -> Retrait:
        if montant <= 0:
            raise InsufficientRetirableAmountError("Le montant du retrait doit etre strictement positif.")

        try:
            client = Client.objects.select_related("agent").get(id=client_id, deleted_at__isnull=True)
        except Client.DoesNotExist as exc:
            raise ClientNotFoundError("Le client selectionne est introuvable.") from exc

        montant_retirable = ReportingService.get_montant_retirable(client_id=client.id)
        if montant > montant_retirable:
            raise InsufficientRetirableAmountError("Le montant retirable est insuffisant.")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT transactions_create_retrait(%s, %s, %s, %s)",
                    [client.id, montant, getattr(created_by, "id", None), motif],
                )
                row = cursor.fetchone()
        except DatabaseError as exc:
            raise InsufficientRetirableAmountError(str(exc)) from exc

        retrait_id = row[0]
        return Retrait.objects.select_related("client", "cycle", "agent").get(id=retrait_id)
