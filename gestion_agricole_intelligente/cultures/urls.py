from django.urls import path

from . import views

app_name = "cultures"

urlpatterns = [
    path("", views.liste_cultures, name="liste"),
    path("ajouter/", views.ajouter_culture, name="ajouter"),
    path("<int:pk>/", views.consulter_culture, name="detail"),
    path("<int:pk>/modifier/", views.modifier_culture, name="modifier"),
    path("<int:pk>/supprimer/", views.supprimer_culture, name="supprimer"),
]