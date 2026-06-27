from django.contrib import admin

from .models import Recommandation


@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = ("culture", "dateRecommandation", "type")
    list_filter = ("dateRecommandation", "culture__agriculteur")
    search_fields = ("culture__nom", "type", "contenu")
