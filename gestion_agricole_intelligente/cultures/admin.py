from django.contrib import admin

from .models import Culture


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "agriculteur",
        "superficie",
        "date_semis",
        "statut",
    )
    search_fields = (
        "nom",
        "localisation",
        "statut",
    )
    list_filter = (
        "date_semis",
        "statut",
    )