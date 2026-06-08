import logging

from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import UserRole
from apps.accounts.permissions import role_required
from apps.agents.forms import AgentCreateForm, AgentUpdateForm
from apps.agents.models import Agent
from apps.agents.services import AgentService
from apps.transactions.services import ReportingService

logger = logging.getLogger("apps.agents.views")


@role_required(UserRole.ADMIN)
def admin_agent_list(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AgentCreateForm(request.POST)
        if form.is_valid():
            agent = AgentService.create_agent(
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telephone=form.cleaned_data["telephone"],
                email=form.cleaned_data["email"],
                adresse=form.cleaned_data["adresse"],
                created_by=request.user,
            )
            logger.info(
                "Agent cree depuis l'interface admin",
                extra={"agent_id": agent.id, "agent_code": agent.code, "created_by": request.user.id},
            )
            messages.success(
                request,
                f"Agent {agent.code} cree avec succes. Mot de passe initial : {AgentService.DEFAULT_PASSWORD}",
            )
            return redirect("admin_agent_detail", agent_id=agent.id)
        modal_open = True
    else:
        form = AgentCreateForm()
        modal_open = False

    agents = (
        Agent.objects.select_related("user")
        .filter(deleted_at__isnull=True)
        .annotate(
            client_count=Count("clients", distinct=True),
            cycle_count=Count("clients__cycles", distinct=True),
        )
        .order_by("code")
    )
    return render(
        request,
        "agents/admin_list.html",
        {
            "agents": agents,
            "form": form,
            "agent_modal_open": modal_open,
            "default_agent_password": AgentService.DEFAULT_PASSWORD,
        },
    )


@role_required(UserRole.ADMIN)
def admin_agent_create(request: HttpRequest) -> HttpResponse:
    return redirect("admin_agent_list")


@role_required(UserRole.ADMIN)
def admin_agent_update(request: HttpRequest, agent_id: int) -> HttpResponse:
    agent = get_object_or_404(Agent.objects.select_related("user"), id=agent_id, deleted_at__isnull=True)

    if request.method == "POST":
        form = AgentUpdateForm(request.POST, user=agent.user)
        if form.is_valid():
            AgentService.update_agent(
                agent,
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telephone=form.cleaned_data["telephone"],
                email=form.cleaned_data["email"],
                adresse=form.cleaned_data["adresse"],
                updated_by=request.user,
            )
            logger.info(
                "Agent modifie depuis l'interface admin",
                extra={"agent_id": agent.id, "agent_code": agent.code, "updated_by": request.user.id},
            )
            messages.success(request, f"Agent {agent.code} modifie avec succes.")
            return redirect("admin_agent_detail", agent_id=agent.id)
    else:
        form = AgentUpdateForm(
            user=agent.user,
            initial={
                "username": agent.user.username,
                "first_name": agent.user.first_name,
                "last_name": agent.user.last_name,
                "telephone": agent.telephone,
                "email": agent.email,
                "adresse": agent.adresse,
            },
        )

    return render(
        request,
        "agents/admin_update.html",
        {
            "agent": agent,
            "form": form,
        },
    )


@role_required(UserRole.ADMIN)
@require_POST
def admin_agent_toggle_status(request: HttpRequest, agent_id: int) -> HttpResponse:
    agent = get_object_or_404(Agent.objects.select_related("user"), id=agent_id, deleted_at__isnull=True)
    AgentService.toggle_active(agent, updated_by=request.user)
    logger.info(
        "Statut agent modifie depuis l'interface admin",
        extra={"agent_id": agent.id, "agent_code": agent.code, "updated_by": request.user.id, "actif": agent.actif},
    )
    if agent.actif:
        messages.success(request, f"Agent {agent.code} debloque avec succes.")
    else:
        messages.success(request, f"Agent {agent.code} bloque avec succes.")
    return redirect(request.POST.get("next") or "admin_agent_list")


@role_required(UserRole.ADMIN)
@require_POST
def admin_agent_delete(request: HttpRequest, agent_id: int) -> HttpResponse:
    agent = get_object_or_404(Agent.objects.select_related("user"), id=agent_id, deleted_at__isnull=True)
    AgentService.soft_delete(agent, deleted_by=request.user)
    logger.info(
        "Agent supprime logiquement depuis l'interface admin",
        extra={"agent_id": agent.id, "agent_code": agent.code, "deleted_by": request.user.id},
    )
    messages.success(request, f"Agent {agent.code} supprime avec succes.")
    return redirect(request.POST.get("next") or "admin_agent_list")


@role_required(UserRole.ADMIN)
def admin_agent_detail(request: HttpRequest, agent_id: int) -> HttpResponse:
    agent = get_object_or_404(
        Agent.objects.select_related("user").annotate(
            client_count=Count("clients", distinct=True),
            active_cycle_count=Count("clients__cycles", distinct=True),
        ),
        id=agent_id,
        deleted_at__isnull=True,
    )
    recent_clients = agent.clients.filter(deleted_at__isnull=True).order_by("nom", "prenom")[:6]
    commission_rows = ReportingService.list_agent_commissions(agent_id=agent.id)
    commission_summary = commission_rows[0] if commission_rows else {"total_commissions": 0, "nb_commissions": 0}
    total_retraits = (
        agent.retraits.filter(deleted_at__isnull=True).aggregate(total=Sum("montant"))["total"] or 0
    )
    return render(
        request,
        "agents/admin_detail.html",
        {
            "agent": agent,
            "recent_clients": recent_clients,
            "commission_summary": commission_summary,
            "total_retraits": total_retraits,
        },
    )
