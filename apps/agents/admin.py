from django.contrib import admin

from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("code", "user", "telephone", "actif", "created_at")
    list_filter = ("actif",)
    search_fields = ("code", "user__username", "user__first_name", "user__last_name")
