from django.contrib import admin

from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "culture",
        "datePrediction",
        "rendementEstime",
        "niveauConfiance",
    )
    list_filter = ("datePrediction", "culture__agriculteur")
    search_fields = ("culture__nom", "commentaires")
