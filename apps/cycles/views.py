import logging

from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import UserRole
from apps.accounts.permissions import role_required
from apps.agents.services import AgentService
from apps.clients.models import Client
from apps.core.exceptions import BusinessRuleError
from apps.core.identifiers import generate_business_code
from apps.cycles.forms import CycleCreateForm
from apps.cycles.models import Cycle
from apps.cycles.services import CycleService
from apps.transactions.models import Depot, Mouvement

logger = logging.getLogger("apps.cycles.views")


def _cycle_detail_context(*, cycle, layout_template: str, back_url: str, is_agent_space: bool) -> dict:
    depots = Depot.objects.filter(cycle=cycle, deleted_at__isnull=True).order_by("-date_depot")
    mouvements = (
        Mouvement.objects.filter(cycle=cycle, deleted_at__isnull=True)
        .select_related("client", "agent")
        .order_by("-date_mouvement")
    )
    return {
        "layout_template": layout_template,
        "back_url": back_url,
        "cycle": cycle,
        "depots": depots,
        "mouvements": mouvements,
        "progress_percent": int((cycle.nb_collectes / 31) * 100),
        "total_collecte_courant": cycle.mise * cycle.nb_collectes,
        "is_agent_space": is_agent_space,
    }


@role_required(UserRole.ADMIN)
def admin_cycle_list(request):
    cycles = (
        Cycle.objects.select_related("client__agent__user")
        .filter(deleted_at__isnull=True)
        .annotate(depot_count=Count("depots", distinct=True))
        .order_by("-date_ouverture")
    )
    return render(request, "cycles/admin_list.html", {"cycles": cycles})


@role_required(UserRole.ADMIN)
def admin_cycle_detail(request, cycle_id: int):
    cycle = get_object_or_404(
        Cycle.objects.select_related("client__agent__user"),
        id=cycle_id,
        deleted_at__isnull=True,
    )
    return render(
        request,
        "cycles/detail.html",
        _cycle_detail_context(
            cycle=cycle,
            layout_template="layouts/admin_layout.html",
            back_url="admin_cycle_list",
            is_agent_space=False,
        ),
    )


@role_required(UserRole.AGENT)
def agent_cycle_list(request):
    agent = AgentService.get_agent_for_user(request.user)
    cycles = (
        Cycle.objects.select_related("client__agent__user")
        .filter(client__agent=agent, deleted_at__isnull=True)
        .annotate(depot_count=Count("depots", distinct=True))
        .order_by("-date_ouverture")
    )
    return render(request, "cycles/agent_list.html", {"cycles": cycles, "agent": agent})


@role_required(UserRole.AGENT)
def agent_cycle_create(request, client_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    client = get_object_or_404(Client, id=client_id, agent=agent, deleted_at__isnull=True)

    if request.method == "POST":
        form = CycleCreateForm(request.POST)
        if form.is_valid():
            try:
                cycle = CycleService.create_cycle(
                    code=generate_business_code("CYC"),
                    client_id=client.id,
                    mise=form.cleaned_data["mise"],
                    created_by=request.user,
                )
            except BusinessRuleError as exc:
                logger.warning(
                    "Cycle refuse par regle metier",
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
                    "Cycle cree depuis l'espace agent",
                    extra={
                        "cycle_id": cycle.id,
                        "cycle_code": cycle.code,
                        "client_id": client.id,
                        "agent_id": agent.id,
                        "created_by": request.user.id,
                    },
                )
                messages.success(request, "Cycle ouvert avec succes.")
                return redirect("agent_cycle_detail", cycle_id=cycle.id)
    else:
        form = CycleCreateForm()

    return render(request, "cycles/agent_create.html", {"form": form, "client": client})


@role_required(UserRole.AGENT)
def agent_cycle_detail(request, cycle_id: int):
    agent = AgentService.get_agent_for_user(request.user)
    cycle = get_object_or_404(
        Cycle.objects.select_related("client__agent__user"),
        id=cycle_id,
        client__agent=agent,
        deleted_at__isnull=True,
    )
    return render(
        request,
        "cycles/detail.html",
        _cycle_detail_context(
            cycle=cycle,
            layout_template="layouts/agent_layout.html",
            back_url="agent_cycle_list",
            is_agent_space=True,
        ),
    )
