from functools import wraps
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

logger = logging.getLogger("apps.accounts.permissions")


def role_required(*allowed_roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                logger.warning(
                    "Acces refuse",
                    extra={
                        "user_id": request.user.id,
                        "username": request.user.username,
                        "role": request.user.role,
                        "path": request.path,
                        "allowed_roles": ",".join(allowed_roles),
                    },
                )
                raise PermissionDenied("Vous n'etes pas autorise a acceder a cette ressource.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
