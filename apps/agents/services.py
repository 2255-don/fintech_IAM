from datetime import date

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.agents.models import Agent


User = get_user_model()


class AgentService:
    DEFAULT_PASSWORD = "password!"

    @staticmethod
    def get_agent_for_user(user) -> Agent:
        return Agent.objects.select_related("user").get(user=user, deleted_at__isnull=True)

    @classmethod
    def generate_next_code(cls) -> str:
        current_year = date.today().year
        prefix = f"AG-{current_year}-"
        codes = Agent.objects.filter(code__startswith=prefix).values_list("code", flat=True)

        max_sequence = 0
        for code in codes:
            try:
                sequence = int(str(code).split("-")[-1])
            except (TypeError, ValueError):
                continue
            max_sequence = max(max_sequence, sequence)

        return f"{prefix}{max_sequence + 1:04d}"

    @classmethod
    @transaction.atomic
    def create_agent(
        cls,
        *,
        username: str,
        password: str | None = None,
        first_name: str,
        last_name: str,
        code: str | None = None,
        telephone: str = "",
        email: str = "",
        adresse: str = "",
        created_by=None,
    ) -> Agent:
        resolved_password = password or cls.DEFAULT_PASSWORD
        resolved_code = code or cls.generate_next_code()

        user = User.objects.create_user(
            username=username,
            password=resolved_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=UserRole.AGENT,
        )
        return Agent.objects.create(
            user=user,
            code=resolved_code,
            telephone=telephone,
            email=email,
            adresse=adresse,
            created_by=created_by,
            updated_by=created_by,
        )

    @classmethod
    @transaction.atomic
    def update_agent(
        cls,
        agent: Agent,
        *,
        username: str,
        first_name: str,
        last_name: str,
        telephone: str = "",
        email: str = "",
        adresse: str = "",
        updated_by=None,
    ) -> Agent:
        agent.user.username = username
        agent.user.first_name = first_name
        agent.user.last_name = last_name
        agent.user.email = email
        agent.user.save(update_fields=["username", "first_name", "last_name", "email"])

        agent.telephone = telephone
        agent.email = email
        agent.adresse = adresse
        agent.updated_by = updated_by
        agent.save(update_fields=["telephone", "email", "adresse", "updated_by", "updated_at"])
        return agent

    @classmethod
    @transaction.atomic
    def toggle_active(cls, agent: Agent, *, updated_by=None) -> Agent:
        agent.actif = not agent.actif
        agent.updated_by = updated_by
        agent.user.is_active = agent.actif
        agent.user.save(update_fields=["is_active"])
        agent.save(update_fields=["actif", "updated_by", "updated_at"])
        return agent

    @classmethod
    @transaction.atomic
    def soft_delete(cls, agent: Agent, *, deleted_by=None) -> Agent:
        timestamp = timezone.now()
        agent.deleted_at = timestamp
        agent.deleted_by = deleted_by
        agent.updated_by = deleted_by
        agent.actif = False
        agent.user.is_active = False
        agent.user.save(update_fields=["is_active"])
        agent.save(update_fields=["deleted_at", "deleted_by", "updated_by", "actif", "updated_at"])
        return agent
