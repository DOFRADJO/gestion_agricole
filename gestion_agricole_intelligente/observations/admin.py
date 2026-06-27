from django.contrib import admin

from .models import Observation


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        "culture",
        "date_observation",
        "description",
    )
    search_fields = (
        "culture__nom",
        "description",
    )
    list_filter = (
        "date_observation",
    )
