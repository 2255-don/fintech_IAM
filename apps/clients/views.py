import logging

from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import UserRole
from apps.accounts.permissions import role_required
from apps.agents.services import AgentService
from apps.clients.forms import ClientCreateForm, ClientUpdateForm
from apps.clients.models import Client
from apps.clients.services import ClientService
from apps.core.identifiers import generate_business_code
from apps.cycles.models import CycleStatus
from apps.transactions.models import Mouvement
from apps.transactions.services import ReportingService

logger = logging.getLogger("apps.clients.views")


def _client_detail_context(*, client, layout_template: str, back_url: str, is_agent_space: bool) -> dict:
    cycles = client.cycles.filter(deleted_at__isnull=True).order_by("-created_at")
    current_active_cycle = cycles.filter(statut=CycleStatus.EN_COURS).first()
    closed_cycles = cycles.filter(statut=CycleStatus.CLOTURE)
    early_closed_cycles = cycles.filter(statut=CycleStatus.CLOTURE_ANTICIPEE)
    recent_mouvements = (
        Mouvement.objects.filter(client=client, deleted_at__isnull=True)
        .select_related("cycle", "agent")
        .order_by("-date_mouvement")[:8]
    )
    last_mouvement = recent_mouvements[0] if recent_mouvements else None

    return {
        "layout_template": layout_template,
        "back_url": back_url,
        "client": client,
        "cycles": cycles,
        "current_active_cycle": current_active_cycle,
        "can_open_cycle": current_active_cycle is None,
        "recent_mouvements": recent_mouvements,
        "last_mouvement": last_mouvement,
        "financial_summary": ReportingService.get_client_financial_summary(client_id=client.id),
        "cycle_metrics": {
            "total_cycles": cycles.count(),
            "active_cycles": 1 if current_active_cycle else 0,
            "closed_cycles": closed_cycles.count(),
            "early_closed_cycles": early_closed_cycles.count(),
        },
        "is_agent_space": is_agent_space,
    }


@role_required(UserRole.ADMIN)
def admin_client_list(request):
    clients = (
        Client.objects.select_related("agent__user")
        .filter(deleted_at__isnull=True)
        .annotate(cycle_count=Count("cycles", distinct=True))
        .order_by("nom", "prenom")
    )
    return render(request, "clients/admin_list.html", {"clients": clients})


@role_required(UserRole.ADMIN)
def admin_client_detail(request, client_id: int):
    client = get_object_or_404(
        Client.objects.select_related("agent__user"),
        id=client_id,
        deleted_at__isnull=True,
    )
    return render(
        request,
        "clients/detail.html",
        _client_detail_context(
            client=client,
            layout_template="layouts/admin_layout.html",
            back_url="admin_client_list",
            is_agent_space=False,
        ),
    )


@role_required(UserRole.AGENT)
def agent_client_list(request):
    agent = AgentService.get_agent_for_user(request.user)
    clients = (
        Client.objects.select_related("agent__user")
        .filter(agent=agent, deleted_at__isnull=True)
        .annotate(cycle_count=Count("cycles", distinct=True))
        .order_by("nom", "prenom")
    )
    return render(request, "clients/agent_list.html", {"clients": clients, "agent": agent})


@role_required(UserRole.AGENT)
def agent_client_create(request):
    agent = AgentService.get_agent_for_user(request.user)
    if request.method == "POST":
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            client = ClientService.create_client(
                code=generate_business_code("CLI"),
                agent_id=agent.id,
                nom=form.cleaned_data["nom"],
                prenom=form.cleaned_data["prenom"],
                telephone=form.cleaned_data["telephone"],
                genre=form.cleaned_data["genre"],
                date_naissance=form.cleaned_data["date_naissance"],
                email=form.cleaned_data["email"],
                adresse=form.cleaned_data["adresse"],
                created_by=request.user,
            )
            logger.info(
                "Client cree depuis l'espace agent",
                extra={
                    "client_id": client.id,
                    "client_code": client.code,
                    "agent_id": agent.id,
                    "created_by": request.user.id,
                },
            )
            messages.success(request, "Client créé avec succès.")
            return redirect("agent_client_detail", client_id=client.id)
    else:
        form = ClientCreateForm()

    return render(request, "clients/agent_create.html", {"form": form, "agent": agent})


@role_required(UserRole.AGENT)
def agent_client_detail(request, client_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    client = get_object_or_404(
        Client.objects.select_related("agent__user"),
        id=client_id,
        agent=agent,
        deleted_at__isnull=True,
    )
    return render(
        request,
        "clients/detail.html",
        _client_detail_context(
            client=client,
            layout_template="layouts/agent_layout.html",
            back_url="agent_client_list",
            is_agent_space=True,
        ),
    )


@role_required(UserRole.AGENT)
def agent_client_update(request, client_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    client = get_object_or_404(
        Client.objects.select_related("agent__user"),
        id=client_id,
        agent=agent,
        deleted_at__isnull=True,
    )

    if request.method == "POST":
        form = ClientUpdateForm(request.POST)
        if form.is_valid():
            ClientService.update_client(
                client,
                nom=form.cleaned_data["nom"],
                prenom=form.cleaned_data["prenom"],
                telephone=form.cleaned_data["telephone"],
                genre=form.cleaned_data["genre"],
                date_naissance=form.cleaned_data["date_naissance"],
                email=form.cleaned_data["email"],
                adresse=form.cleaned_data["adresse"],
                updated_by=request.user,
            )
            logger.info(
                "Client modifie depuis l'espace agent",
                extra={
                    "client_id": client.id,
                    "client_code": client.code,
                    "agent_id": agent.id,
                    "updated_by": request.user.id,
                },
            )
            messages.success(request, f"Les informations de {client.code} ont été mises à jour avec succès.")
            return redirect("agent_client_detail", client_id=client.id)
    else:
        form = ClientUpdateForm(
            initial={
                "nom": client.nom,
                "prenom": client.prenom,
                "telephone": client.telephone,
                "genre": client.genre,
                "date_naissance": client.date_naissance,
                "email": client.email,
                "adresse": client.adresse,
            }
        )

    return render(request, "clients/agent_update.html", {"form": form, "client": client})
