from django.urls import path

from .views import (
    UserLoginView,
    UserLogoutView,
    admin_dashboard,
    agent_dashboard,
    dashboard_redirect,
)


urlpatterns = [
    path("connexion/", UserLoginView.as_view(), name="login"),
    path("deconnexion/", UserLogoutView.as_view(), name="logout"),
    path("tableau-de-bord/", dashboard_redirect, name="dashboard_redirect"),
    path("tableau-de-bord/admin/", admin_dashboard, name="admin_dashboard"),
    path("tableau-de-bord/agent/", agent_dashboard, name="agent_dashboard"),
]
