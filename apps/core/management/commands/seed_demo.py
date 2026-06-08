from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.agents.services import AgentService
from apps.clients.models import Client
from apps.clients.services import ClientService
from apps.core.identifiers import generate_business_code
from apps.cycles.models import Cycle
from apps.cycles.services import CycleService
from apps.transactions.models import Depot, Retrait
from apps.transactions.services import DepotService, RetraitService


User = get_user_model()


class Command(BaseCommand):
    help = "Cree un jeu de donnees minimum pour la demonstration fonctionnelle du projet."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._ensure_admin()
        agent_alpha = self._ensure_agent(
            created_by=admin,
            username="agent_alpha",
            password="AgentDemo123!",
            first_name="Awa",
            last_name="Diallo",
            code="AG-DEMO-001",
            telephone="70000001",
            email="agent.alpha@fintech-iam.local",
            adresse="Bamako - Commune I",
        )
        agent_beta = self._ensure_agent(
            created_by=admin,
            username="agent_beta",
            password="AgentDemo123!",
            first_name="Moussa",
            last_name="Traore",
            code="AG-DEMO-002",
            telephone="70000002",
            email="agent.beta@fintech-iam.local",
            adresse="Bamako - Commune IV",
        )

        client_alpha_1 = self._ensure_client(
            created_by=admin,
            agent=agent_alpha,
            code="CLI-DEMO-001",
            nom="Konate",
            prenom="Fatoumata",
            telephone="71000001",
            genre="F",
            date_naissance=date(1994, 3, 14),
            email="fatoumata.konate@demo.local",
            adresse="Sebenikoro",
        )
        client_alpha_2 = self._ensure_client(
            created_by=admin,
            agent=agent_alpha,
            code="CLI-DEMO-002",
            nom="Keita",
            prenom="Boubacar",
            telephone="71000002",
            genre="M",
            date_naissance=date(1989, 7, 2),
            email="boubacar.keita@demo.local",
            adresse="Kalaban Coura",
        )
        client_beta_1 = self._ensure_client(
            created_by=admin,
            agent=agent_beta,
            code="CLI-DEMO-003",
            nom="Sissoko",
            prenom="Aminata",
            telephone="71000003",
            genre="F",
            date_naissance=date(1998, 11, 19),
            email="aminata.sissoko@demo.local",
            adresse="Lafiabougou",
        )

        cycle_alpha_1 = self._ensure_cycle(
            created_by=admin,
            client=client_alpha_1,
            code="CYC-DEMO-001",
            mise=1000,
        )
        cycle_alpha_2 = self._ensure_cycle(
            created_by=admin,
            client=client_alpha_2,
            code="CYC-DEMO-002",
            mise=2000,
        )
        cycle_beta_1 = self._ensure_cycle(
            created_by=admin,
            client=client_beta_1,
            code="CYC-DEMO-003",
            mise=1500,
        )

        self._ensure_depot(
            created_by=admin,
            cycle=cycle_alpha_1,
            code="DEP-DEMO-001",
            nb_mises=12,
        )
        self._ensure_depot(
            created_by=admin,
            cycle=cycle_alpha_2,
            code="DEP-DEMO-002",
            nb_mises=31,
        )
        self._ensure_depot(
            created_by=admin,
            cycle=cycle_beta_1,
            code="DEP-DEMO-003",
            nb_mises=7,
        )

        self._ensure_retrait(
            created_by=admin,
            client=client_alpha_2,
            montant=5000,
            motif="Retrait de demonstration",
        )

        self.stdout.write(self.style.SUCCESS("Jeu de demonstration cree ou mis a jour avec succes."))
        self.stdout.write("Comptes disponibles :")
        self.stdout.write("  - Admin : admin_demo / AdminDemo123!")
        self.stdout.write("  - Agent : agent_alpha / AgentDemo123!")
        self.stdout.write("  - Agent : agent_beta / AgentDemo123!")

    def _ensure_admin(self):
        user, created = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "first_name": "Admin",
                "last_name": "Demo",
                "email": "admin.demo@fintech-iam.local",
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.first_name = "Admin"
        user.last_name = "Demo"
        user.email = "admin.demo@fintech-iam.local"
        user.role = UserRole.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password("AdminDemo123!")
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Admin de demonstration cree."))
        else:
            self.stdout.write("Admin de demonstration mis a jour.")
        return user

    def _ensure_agent(
        self,
        *,
        created_by,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        code: str,
        telephone: str,
        email: str,
        adresse: str,
    ) -> Agent:
        user = User.objects.filter(username=username).first()
        agent = Agent.objects.filter(code=code).select_related("user").first()

        if user is None and agent is None:
            agent = AgentService.create_agent(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                code=code,
                telephone=telephone,
                email=email,
                adresse=adresse,
                created_by=created_by,
            )
            self.stdout.write(self.style.SUCCESS(f"Agent {code} cree."))
            return agent

        if user is None and agent is not None:
            user = agent.user

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.role = UserRole.AGENT
        user.is_active = True
        user.set_password(password)
        user.save()

        if agent is None:
            agent = Agent.objects.create(
                user=user,
                code=code,
                telephone=telephone,
                email=email,
                adresse=adresse,
                created_by=created_by,
                updated_by=created_by,
            )
        else:
            agent.user = user
            agent.code = code
            agent.telephone = telephone
            agent.email = email
            agent.adresse = adresse
            agent.actif = True
            agent.updated_by = created_by
            agent.save()

        self.stdout.write(f"Agent {code} mis a jour.")
        return agent

    def _ensure_client(
        self,
        *,
        created_by,
        agent: Agent,
        code: str,
        nom: str,
        prenom: str,
        telephone: str,
        genre: str,
        date_naissance,
        email: str,
        adresse: str,
    ) -> Client:
        client = Client.objects.filter(code=code).first()
        if client is None:
            client = ClientService.create_client(
                code=code,
                agent_id=agent.id,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                genre=genre,
                date_naissance=date_naissance,
                email=email,
                adresse=adresse,
                created_by=created_by,
            )
            self.stdout.write(self.style.SUCCESS(f"Client {code} cree."))
            return client

        client.agent = agent
        client.nom = nom
        client.prenom = prenom
        client.telephone = telephone
        client.genre = genre
        client.date_naissance = date_naissance
        client.email = email
        client.adresse = adresse
        client.actif = True
        client.updated_by = created_by
        client.save()
        self.stdout.write(f"Client {code} mis a jour.")
        return client

    def _ensure_cycle(self, *, created_by, client: Client, code: str, mise: int) -> Cycle:
        cycle = Cycle.objects.filter(code=code).first()
        if cycle is None:
            cycle = CycleService.create_cycle(
                code=code,
                client_id=client.id,
                mise=mise,
                created_by=created_by,
            )
            self.stdout.write(self.style.SUCCESS(f"Cycle {code} cree."))
            return cycle

        self.stdout.write(f"Cycle {code} deja present.")
        return cycle

    def _ensure_depot(self, *, created_by, cycle: Cycle, code: str, nb_mises: int) -> Depot | None:
        depot = Depot.objects.filter(code=code).first()
        if depot is not None:
            self.stdout.write(f"Depot {code} deja present.")
            return depot

        depot = DepotService.create_depot(
            code=code,
            cycle_id=cycle.id,
            nb_mises=nb_mises,
            created_by=created_by,
        )
        self.stdout.write(self.style.SUCCESS(f"Depot {code} cree."))
        return depot

    def _ensure_retrait(self, *, created_by, client: Client, montant: int, motif: str) -> Retrait | None:
        retrait = Retrait.objects.filter(client=client, montant=montant, motif=motif).first()
        if retrait is not None:
            self.stdout.write(f"Retrait demo deja present pour {client.code}.")
            return retrait

        retrait = RetraitService.create_retrait(
            client_id=client.id,
            montant=montant,
            motif=motif,
            created_by=created_by,
        )
        self.stdout.write(self.style.SUCCESS(f"Retrait demo cree pour {client.code}."))
        return retrait
