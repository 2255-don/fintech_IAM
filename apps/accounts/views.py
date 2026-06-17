from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.agents.models import Agent
from apps.agents.services import AgentService
from apps.clients.models import Client
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.models import Mouvement, Retrait
from apps.transactions.services import ReportingService

from .forms import LoginForm
from .models import UserRole
from .permissions import role_required


class UserLoginView(LoginView):
    authentication_form = LoginForm
    redirect_authenticated_user = True
    template_name = "accounts/login.html"

    def get_success_url(self):
        return reverse_lazy("dashboard_redirect")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("login")


def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.role == UserRole.ADMIN:
        return redirect("admin_dashboard")
    return redirect("agent_dashboard")


@role_required(UserRole.ADMIN)
def admin_dashboard(request):
    recent_mouvements = (
        Mouvement.objects.select_related("client", "cycle", "agent")
        .filter(deleted_at__isnull=True)
        .order_by("-date_mouvement")[:6]
    )
    commission_rows = ReportingService.list_agent_commissions()
    total_commissions_agent = sum(row["total_commissions"] for row in commission_rows)
    total_commissions_plateforme = sum(row["total_commissions_plateforme"] for row in commission_rows)
    return render(
        request,
        "accounts/admin_dashboard.html",
        {
            "agent_count": Agent.objects.filter(deleted_at__isnull=True).count(),
            "client_count": Client.objects.filter(deleted_at__isnull=True).count(),
            "cycles_in_progress": Cycle.objects.filter(
                deleted_at__isnull=True,
                statut=CycleStatus.EN_COURS,
            ).count(),
            "cycles_closed": Cycle.objects.filter(
                deleted_at__isnull=True,
                statut=CycleStatus.CLOTURE,
            ).count(),
            "total_commissions_agent": total_commissions_agent,
            "total_commissions_plateforme": total_commissions_plateforme,
            "total_retraits": Retrait.objects.filter(deleted_at__isnull=True).aggregate(total=Sum("montant"))["total"] or 0,
            "recent_mouvements": recent_mouvements,
            "top_clients": ReportingService.list_client_retirable_rows(limit=5),
        },
    )


@role_required(UserRole.AGENT)
def agent_dashboard(request):
    try:
        agent = AgentService.get_agent_for_user(request.user)
    except Agent.DoesNotExist:
        agent = None

    if agent is None:
        recent_mouvements = []
        client_count = 0
        cycles_in_progress = 0
        cycles_closed = 0
        portfolio_retirable = 0
        total_commissions = 0
        top_clients = []
    else:
        recent_mouvements = (
            Mouvement.objects.select_related("client", "cycle", "agent")
            .filter(agent=agent, deleted_at__isnull=True)
            .order_by("-date_mouvement")[:6]
        )
        client_count = Client.objects.filter(agent=agent, deleted_at__isnull=True).count()
        cycles_in_progress = Cycle.objects.filter(
            client__agent=agent,
            deleted_at__isnull=True,
            statut=CycleStatus.EN_COURS,
        ).count()
        cycles_closed = Cycle.objects.filter(
            client__agent=agent,
            deleted_at__isnull=True,
            statut=CycleStatus.CLOTURE,
        ).count()
        portfolio_retirable = ReportingService.get_portfolio_retirable_total(agent_id=agent.id)
        total_commissions = sum(
            row["total_commissions"] for row in ReportingService.list_agent_commissions(agent_id=agent.id)
        )
        top_clients = ReportingService.list_client_retirable_rows(agent_id=agent.id, limit=5)

    return render(
        request,
        "accounts/agent_dashboard.html",
        {
            "agent": agent,
            "client_count": client_count,
            "cycles_in_progress": cycles_in_progress,
            "cycles_closed": cycles_closed,
            "portfolio_retirable": portfolio_retirable,
            "total_commissions": total_commissions,
            "recent_mouvements": recent_mouvements,
            "top_clients": top_clients,
        },
    )
