from django.urls import path

from . import views

app_name = "core"

urlpatterns = [

    path(
        "dashboard/agriculteur/",
        views.dashboard_agriculteur,
        name="dashboard_agriculteur",
    ),

    path(
        "dashboard/agronome/",
        views.dashboard_agronome,
        name="dashboard_agronome",
    ),

    path(
        "dashboard/administrateur/",
        views.dashboard_admin,
        name="dashboard_admin",
    ),

]