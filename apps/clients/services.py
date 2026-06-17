from apps.agents.models import Agent
from apps.clients.models import Client
from apps.core.exceptions import AgentNotFoundError


class ClientService:
    @staticmethod
    def create_client(
        *,
        code: str,
        agent_id: int,
        nom: str,
        telephone: str,
        prenom: str = "",
        genre: str = "",
        date_naissance=None,
        email: str = "",
        adresse: str = "",
        created_by=None,
    ) -> Client:
        try:
            agent = Agent.objects.get(id=agent_id, deleted_at__isnull=True)
        except Agent.DoesNotExist as exc:
            raise AgentNotFoundError("L'agent responsable est introuvable.") from exc

        client = Client.objects.create(
            code=code,
            agent=agent,
            nom=nom,
            prenom=prenom,
            genre=genre,
            date_naissance=date_naissance,
            telephone=telephone,
            email=email,
            adresse=adresse,
            created_by=created_by,
            updated_by=created_by,
        )
        return client

    @staticmethod
    def update_client(
        client: Client,
        *,
        nom: str,
        telephone: str,
        prenom: str = "",
        genre: str = "",
        date_naissance=None,
        email: str = "",
        adresse: str = "",
        updated_by=None,
    ) -> Client:
        client.nom = nom
        client.prenom = prenom
        client.genre = genre
        client.date_naissance = date_naissance
        client.telephone = telephone
        client.email = email
        client.adresse = adresse
        client.updated_by = updated_by
        client.save(
            update_fields=[
                "nom",
                "prenom",
                "genre",
                "date_naissance",
                "telephone",
                "email",
                "adresse",
                "updated_by",
                "updated_at",
            ]
        )
        return client
