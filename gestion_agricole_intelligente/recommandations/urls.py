from django.urls import path

from . import views

app_name = "recommandations"

urlpatterns = [
    path("", views.liste_recommandations, name="liste"),
    path("historique/", views.historique_recommandations, name="historique"),
    path("<int:pk>/", views.detail_recommandation, name="detail"),
]
