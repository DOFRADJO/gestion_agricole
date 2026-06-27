from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from services.dashboard_service import DashboardService


@login_required
def dashboard_agriculteur(request):
    contexte = DashboardService.obtenir_dashboard(request.user)
    return render(
        request,
        "core/dashboard.html",
        contexte,
    )


@login_required
def dashboard_agronome(request):
    contexte = DashboardService.obtenir_dashboard(request.user)
    return render(
        request,
        "core/dashboard.html",
        contexte,
    )


@login_required
def dashboard_admin(request):
    contexte = DashboardService.obtenir_dashboard(request.user)
    return render(
        request,
        "core/dashboard.html",
        contexte,
    )