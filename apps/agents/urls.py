from django.urls import path

from apps.agents.views import (
    admin_agent_create,
    admin_agent_delete,
    admin_agent_detail,
    admin_agent_list,
    admin_agent_toggle_status,
    admin_agent_update,
)


urlpatterns = [
    path("espace-admin/agents/", admin_agent_list, name="admin_agent_list"),
    path("espace-admin/agents/nouveau/", admin_agent_create, name="admin_agent_create"),
    path("espace-admin/agents/<int:agent_id>/", admin_agent_detail, name="admin_agent_detail"),
    path("espace-admin/agents/<int:agent_id>/modifier/", admin_agent_update, name="admin_agent_update"),
    path("espace-admin/agents/<int:agent_id>/statut/", admin_agent_toggle_status, name="admin_agent_toggle_status"),
    path("espace-admin/agents/<int:agent_id>/supprimer/", admin_agent_delete, name="admin_agent_delete"),
]
