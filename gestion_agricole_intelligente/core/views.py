from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_agriculteur(request):

    return render(
        request,
        "core/dashboard_agriculteur.html",
    )


@login_required
def dashboard_agronome(request):

    return render(
        request,
        "core/dashboard_agronome.html",
    )


@login_required
def dashboard_admin(request):

    return render(
        request,
        "core/dashboard_admin.html",
    )