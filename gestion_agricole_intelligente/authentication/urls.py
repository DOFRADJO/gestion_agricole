from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [

    path(
        "",
        views.connexion,
        name="connexion",
    ),

    path(
        "deconnexion/",
        views.deconnexion,
        name="deconnexion",
    ),

]