from django.contrib import admin

from .models import Cycle


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ("code", "client", "mise", "nb_collectes", "statut", "date_ouverture")
    list_filter = ("statut",)
    search_fields = ("code", "client__code", "client__nom", "client__prenom")
