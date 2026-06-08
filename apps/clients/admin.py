from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "prenom", "agent", "telephone", "actif")
    list_filter = ("actif", "agent")
    search_fields = ("code", "nom", "prenom", "telephone")
