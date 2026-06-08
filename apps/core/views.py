from django.http import JsonResponse
from django.shortcuts import redirect, render

from apps.accounts.models import UserRole


def home(request):
    if request.user.is_authenticated:
        if request.user.role == UserRole.ADMIN:
            return redirect("admin_dashboard")
        return redirect("agent_dashboard")
    return render(request, "core/home.html")


def healthcheck(request):
    return JsonResponse({"status": "ok", "service": "fintech-iam"})
