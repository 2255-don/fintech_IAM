from django.contrib import admin

from .models import Depot, Mouvement, Retenue, Retrait


@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ("code", "cycle", "client", "agent", "nb_mises", "montant", "date_depot")
    list_filter = ("agent", "date_depot")
    search_fields = ("code", "client__code", "cycle__code")


@admin.register(Retenue)
class RetenueAdmin(admin.ModelAdmin):
    list_display = ("code", "cycle", "client", "montant", "commission_agent", "commission_institution")
    search_fields = ("code", "client__code", "cycle__code")


@admin.register(Retrait)
class RetraitAdmin(admin.ModelAdmin):
    list_display = ("code", "client", "agent", "montant", "date_retrait")
    list_filter = ("agent", "date_retrait")
    search_fields = ("code", "client__code")


@admin.register(Mouvement)
class MouvementAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "sens", "montant", "client", "cycle", "agent", "date_mouvement")
    list_filter = ("type", "sens", "date_mouvement")
    search_fields = ("code", "client__code", "cycle__code", "reference_operation")
