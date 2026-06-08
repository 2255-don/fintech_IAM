import logging

from django.shortcuts import render


logger = logging.getLogger("apps.core.errors")


def permission_denied_view(request, exception):
    logger.warning(
        "Erreur 403 retournee",
        extra={
            "path": request.path,
            "user_id": getattr(request.user, "id", None),
            "username": getattr(request.user, "username", "anonymous"),
        },
    )
    return render(request, "403.html", status=403)


def page_not_found_view(request, exception):
    logger.warning(
        "Erreur 404 retournee",
        extra={
            "path": request.path,
            "user_id": getattr(request.user, "id", None),
            "username": getattr(request.user, "username", "anonymous"),
        },
    )
    return render(request, "404.html", status=404)


def server_error_view(request):
    logger.exception(
        "Erreur 500 retournee",
        extra={
            "path": request.path,
            "user_id": getattr(request.user, "id", None),
            "username": getattr(request.user, "username", "anonymous"),
        },
    )
    return render(request, "500.html", status=500)
