from django.urls import path

from . import views

app_name = "utilisateurs"

urlpatterns = [
    path(
        "",
        views.liste_utilisateurs,
        name="liste",
    ),
    path(
        "ajouter/",
        views.creer_utilisateur,
        name="ajouter",
    ),
    path(
        "modifier/<int:pk>/",
        views.modifier_utilisateur,
        name="modifier",
    ),
    path(
        "supprimer/<int:pk>/",
        views.supprimer_utilisateur,
        name="supprimer",
    ),
]
