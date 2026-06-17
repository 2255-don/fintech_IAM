from django.urls import path

from apps.clients.views import (
    admin_client_detail,
    admin_client_list,
    agent_client_create,
    agent_client_detail,
    agent_client_list,
    agent_client_update,
)


urlpatterns = [
    path("espace-admin/clients/", admin_client_list, name="admin_client_list"),
    path("espace-admin/clients/<int:client_id>/", admin_client_detail, name="admin_client_detail"),
    path("espace-agent/clients/", agent_client_list, name="agent_client_list"),
    path("espace-agent/clients/nouveau/", agent_client_create, name="agent_client_create"),
    path("espace-agent/clients/<int:client_id>/modifier/", agent_client_update, name="agent_client_update"),
    path("espace-agent/clients/<int:client_id>/", agent_client_detail, name="agent_client_detail"),
]
