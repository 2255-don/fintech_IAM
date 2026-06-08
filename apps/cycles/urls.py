from django.urls import path

from apps.cycles.views import (
    admin_cycle_detail,
    admin_cycle_list,
    agent_cycle_create,
    agent_cycle_detail,
    agent_cycle_list,
)


urlpatterns = [
    path("espace-admin/cycles/", admin_cycle_list, name="admin_cycle_list"),
    path("espace-admin/cycles/<int:cycle_id>/", admin_cycle_detail, name="admin_cycle_detail"),
    path("espace-agent/cycles/", agent_cycle_list, name="agent_cycle_list"),
    path("espace-agent/clients/<int:client_id>/cycles/nouveau/", agent_cycle_create, name="agent_cycle_create"),
    path("espace-agent/cycles/<int:cycle_id>/", agent_cycle_detail, name="agent_cycle_detail"),
]
