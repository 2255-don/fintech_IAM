from django.urls import path

from apps.transactions.views import (
    admin_commission_list,
    admin_depot_list,
    admin_mouvement_list,
    admin_retrait_list,
    agent_commission_list,
    agent_depot_create,
    agent_emergency_withdrawal_create,
    agent_mouvement_list,
    agent_retrait_create,
)


urlpatterns = [
    path("espace-admin/depots/", admin_depot_list, name="admin_depot_list"),
    path("espace-admin/retraits/", admin_retrait_list, name="admin_retrait_list"),
    path("espace-admin/mouvements/", admin_mouvement_list, name="admin_mouvement_list"),
    path("espace-admin/commissions/", admin_commission_list, name="admin_commission_list"),
    path("espace-agent/cycles/<int:cycle_id>/depots/nouveau/", agent_depot_create, name="agent_depot_create"),
    path("espace-agent/clients/<int:client_id>/retraits/nouveau/", agent_retrait_create, name="agent_retrait_create"),
    path(
        "espace-agent/cycles/<int:cycle_id>/retraits/urgence/",
        agent_emergency_withdrawal_create,
        name="agent_emergency_withdrawal_create",
    ),
    path("espace-agent/mouvements/", agent_mouvement_list, name="agent_mouvement_list"),
    path("espace-agent/commissions/", agent_commission_list, name="agent_commission_list"),
]
