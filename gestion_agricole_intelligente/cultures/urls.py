from django.urls import path

from . import views

app_name = "cultures"

urlpatterns = [

    path(

        "",

        views.liste_cultures,

        name="liste",

    ),

    path(

        "ajouter/",

        views.ajouter_culture,

        name="ajouter",

    ),

]