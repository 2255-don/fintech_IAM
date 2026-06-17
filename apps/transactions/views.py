import logging

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import UserRole
from apps.accounts.permissions import role_required
from apps.agents.services import AgentService
from apps.clients.models import Client
from apps.core.exceptions import BusinessRuleError
from apps.core.identifiers import generate_business_code
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.calculations import calculate_emergency_withdrawal_distribution
from apps.transactions.forms import DepotCreateForm, EmergencyWithdrawalForm, RetraitCreateForm
from apps.transactions.models import Depot, Mouvement, Retrait
from apps.transactions.services import (
    DepotService,
    EmergencyWithdrawalService,
    ReportingService,
    RetraitService,
)

logger = logging.getLogger("apps.transactions.views")


@role_required(UserRole.ADMIN)
def admin_depot_list(request):
    depots = (
        Depot.objects.select_related("cycle", "client", "agent")
        .filter(deleted_at__isnull=True)
        .order_by("-date_depot")
    )
    return render(request, "transactions/admin_depot_list.html", {"depots": depots})


@role_required(UserRole.ADMIN)
def admin_retrait_list(request):
    retraits = (
        Retrait.objects.select_related("client", "cycle", "agent")
        .filter(deleted_at__isnull=True)
        .order_by("-date_retrait")
    )
    return render(request, "transactions/admin_retrait_list.html", {"retraits": retraits})


@role_required(UserRole.ADMIN)
def admin_mouvement_list(request):
    mouvements = (
        Mouvement.objects.select_related("client", "cycle", "agent")
        .filter(deleted_at__isnull=True)
        .order_by("-date_mouvement")
    )
    return render(request, "transactions/admin_mouvement_list.html", {"mouvements": mouvements})


@role_required(UserRole.ADMIN)
def admin_commission_list(request):
    commission_rows = ReportingService.list_agent_commissions()
    total_commissions_agent = sum(row["total_commissions"] for row in commission_rows)
    total_commissions_plateforme = sum(row["total_commissions_plateforme"] for row in commission_rows)
    return render(
        request,
        "transactions/admin_commission_list.html",
        {
            "commission_rows": commission_rows,
            "total_commissions_agent": total_commissions_agent,
            "total_commissions_plateforme": total_commissions_plateforme,
        },
    )


@role_required(UserRole.AGENT)
def agent_depot_create(request, cycle_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    cycle = get_object_or_404(
        Cycle.objects.select_related("client__agent"),
        id=cycle_id,
        client__agent=agent,
        deleted_at__isnull=True,
    )

    if request.method == "POST":
        form = DepotCreateForm(request.POST)
        if form.is_valid():
            try:
                depot = DepotService.create_depot(
                    code=generate_business_code("DEP"),
                    cycle_id=cycle.id,
                    nb_mises=form.cleaned_data["nb_mises"],
                    created_by=request.user,
                )
            except BusinessRuleError as exc:
                logger.warning(
                    "Depot refuse par regle metier",
                    extra={
                        "cycle_id": cycle.id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "reason": str(exc),
                    },
                )
                form.add_error(None, str(exc))
            else:
                cycle.refresh_from_db()
                logger.info(
                    "Depot cree depuis l'espace agent",
                    extra={
                        "depot_id": depot.id,
                        "cycle_id": depot.cycle_id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "nb_mises": form.cleaned_data["nb_mises"],
                        "cycle_status": cycle.statut,
                    },
                )
                if cycle.statut == CycleStatus.CLOTURE:
                    messages.success(request, "Depot enregistre avec succes. Le cycle a ete cloture automatiquement.")
                else:
                    messages.success(request, "Depot enregistre avec succes.")
                return redirect("agent_cycle_detail", cycle_id=depot.cycle_id)
    else:
        form = DepotCreateForm()

    return render(request, "transactions/agent_depot_create.html", {"form": form, "cycle": cycle})


@role_required(UserRole.AGENT)
def agent_retrait_create(request, client_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    client = get_object_or_404(
        Client.objects.select_related("agent"),
        id=client_id,
        agent=agent,
        deleted_at__isnull=True,
    )
    financial_summary = ReportingService.get_client_financial_summary(client_id=client.id)

    if request.method == "POST":
        form = RetraitCreateForm(request.POST)
        if form.is_valid():
            try:
                retrait = RetraitService.create_retrait(
                    client_id=client.id,
                    montant=form.cleaned_data["montant"],
                    motif=form.cleaned_data["motif"],
                    created_by=request.user,
                )
            except BusinessRuleError as exc:
                logger.warning(
                    "Retrait refuse par regle metier",
                    extra={
                        "client_id": client.id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "reason": str(exc),
                    },
                )
                form.add_error(None, str(exc))
            else:
                logger.info(
                    "Retrait cree depuis l'espace agent",
                    extra={
                        "retrait_id": retrait.id,
                        "client_id": retrait.client_id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "montant": form.cleaned_data["montant"],
                    },
                )
                messages.success(request, "Retrait enregistre avec succes.")
                return redirect("agent_client_detail", client_id=retrait.client_id)
    else:
        form = RetraitCreateForm()

    return render(
        request,
        "transactions/agent_retrait_create.html",
        {"form": form, "client": client, "financial_summary": financial_summary},
    )


@role_required(UserRole.AGENT)
def agent_emergency_withdrawal_create(request, cycle_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    cycle = get_object_or_404(
        Cycle.objects.select_related("client__agent"),
        id=cycle_id,
        client__agent=agent,
        deleted_at__isnull=True,
    )
    emergency_summary = calculate_emergency_withdrawal_distribution(
        mise=cycle.mise,
        nb_collectes=cycle.nb_collectes,
        montant=0,
    )

    if request.method == "POST":
        form = EmergencyWithdrawalForm(request.POST)
        if form.is_valid():
            try:
                result = EmergencyWithdrawalService.create_emergency_withdrawal(
                    cycle_id=cycle.id,
                    montant=form.cleaned_data["montant"],
                    motif=form.cleaned_data["motif"],
                    created_by=request.user,
                )
            except BusinessRuleError as exc:
                logger.warning(
                    "Retrait d'urgence refuse par regle metier",
                    extra={
                        "cycle_id": cycle.id,
                        "client_id": cycle.client_id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "reason": str(exc),
                    },
                )
                form.add_error(None, str(exc))
            else:
                logger.info(
                    "Retrait d'urgence cree depuis l'espace agent",
                    extra={
                        "retrait_id": result.retrait.id,
                        "cycle_id": cycle.id,
                        "client_id": cycle.client_id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                        "montant": form.cleaned_data["montant"],
                        "penalite": result.penalite,
                        "credit_client": result.credit_client,
                    },
                )
                if result.credit_client > 0:
                    messages.success(
                        request,
                        f"Retrait d'urgence enregistre. Le cycle est cloture par anticipation et {result.credit_client} FCFA restent disponibles pour un retrait classique.",
                    )
                else:
                    messages.success(
                        request,
                        "Retrait d'urgence enregistre. Le cycle est cloture par anticipation.",
                    )
                return redirect("agent_client_detail", client_id=cycle.client_id)
    else:
        form = EmergencyWithdrawalForm()

    return render(
        request,
        "transactions/agent_emergency_withdrawal_create.html",
        {
            "form": form,
            "cycle": cycle,
            "client": cycle.client,
            "emergency_summary": emergency_summary,
        },
    )


@role_required(UserRole.AGENT)
def agent_mouvement_list(request):
    agent = AgentService.get_agent_for_user(request.user)
    mouvements = (
        Mouvement.objects.select_related("client", "cycle", "agent")
        .filter(agent=agent, deleted_at__isnull=True)
        .order_by("-date_mouvement")
    )
    return render(request, "transactions/agent_mouvement_list.html", {"mouvements": mouvements, "agent": agent})


@role_required(UserRole.AGENT)
def agent_commission_list(request):
    agent = AgentService.get_agent_for_user(request.user)
    commission_rows = ReportingService.list_agent_commissions(agent_id=agent.id)
    total_commissions = sum(row["total_commissions"] for row in commission_rows)
    portfolio_retirable = ReportingService.get_portfolio_retirable_total(agent_id=agent.id)
    total_retraits = (
        Retrait.objects.filter(agent=agent, deleted_at__isnull=True).aggregate(total=Sum("montant"))["total"] or 0
    )
    return render(
        request,
        "transactions/agent_commission_list.html",
        {
            "commission_rows": commission_rows,
            "total_commissions": total_commissions,
            "portfolio_retirable": portfolio_retirable,
            "total_retraits": total_retraits,
            "agent": agent,
        },
    )
