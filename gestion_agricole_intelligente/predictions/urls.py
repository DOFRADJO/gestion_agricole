from django.urls import path

from . import views

app_name = "predictions"

urlpatterns = [
    path("", views.liste_predictions, name="liste"),
    path("historique/", views.historique_predictions, name="historique"),
    path("<int:pk>/", views.detail_prediction, name="detail"),
]
