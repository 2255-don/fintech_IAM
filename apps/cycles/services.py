from apps.clients.models import Client
from apps.core.exceptions import ActiveCycleAlreadyExistsError, ClientNotFoundError, InvalidMiseError
from apps.cycles.models import Cycle, CycleStatus


class CycleService:
    @staticmethod
    def validate_mise(mise: int) -> None:
        if mise <= 0:
            raise InvalidMiseError("La mise doit etre strictement positive.")
        if mise % 100 != 0:
            raise InvalidMiseError("La mise doit etre un multiple de 100 FCFA.")

    @classmethod
    def create_cycle(
        cls,
        *,
        code: str,
        client_id: int,
        mise: int,
        created_by=None,
    ) -> Cycle:
        cls.validate_mise(mise)

        try:
            client = Client.objects.get(id=client_id, deleted_at__isnull=True)
        except Client.DoesNotExist as exc:
            raise ClientNotFoundError("Le client selectionne est introuvable.") from exc

        if Cycle.objects.filter(
            client=client,
            statut=CycleStatus.EN_COURS,
            deleted_at__isnull=True,
        ).exists():
            raise ActiveCycleAlreadyExistsError("Un cycle est deja en cours pour ce client.")

        cycle = Cycle.objects.create(
            code=code,
            client=client,
            mise=mise,
            nb_collectes=0,
            statut=CycleStatus.EN_COURS,
            created_by=created_by,
            updated_by=created_by,
        )
        return cycle
