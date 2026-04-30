from django.contrib import admin

from manage_breast_screening.core.admin import admin_site

from .models import Gateway, Relay


@admin.register(Gateway, site=admin_site)
class GatewayAdmin(admin.ModelAdmin):
    list_display = ["name", "oid", "resource_name"]
    search_fields = ["name", "oid", "resource_name"]
    list_filter = ["created_at", "updated_at"]
    ordering = ["name"]


@admin.register(Relay, site=admin_site)
class RelayAdmin(admin.ModelAdmin):
    list_display = ["setting", "gateway", "namespace", "hybrid_connection_name"]
    list_select_related = ["setting", "gateway"]
    search_fields = [
        "setting__name",
        "gateway__name",
        "namespace",
        "hybrid_connection_name",
    ]
    list_filter = ["created_at", "updated_at"]
    ordering = ["setting__name", "gateway__name", "namespace", "hybrid_connection_name"]
