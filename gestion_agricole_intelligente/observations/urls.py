from django.urls import path
from . import views

app_name = "observations"

urlpatterns = [
    path("", views.liste_observations, name="liste"),
    path("ajouter/", views.ajouter_observation, name="ajouter"),
    path("<int:pk>/", views.consulter_observation, name="detail"),
    path("<int:pk>/modifier/", views.modifier_observation, name="modifier"),
    path("<int:pk>/supprimer/", views.supprimer_observation, name="supprimer"),
]
