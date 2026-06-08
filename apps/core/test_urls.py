from django.http import HttpResponse
from django.urls import include, path


def trigger_server_error(request):
    raise RuntimeError("test server error")


def ok_view(request):
    return HttpResponse("ok")


urlpatterns = [
    path("", include("config.urls")),
    path("__test-error-500/", trigger_server_error, name="test_error_500"),
    path("__test-ok/", ok_view, name="test_ok"),
]
