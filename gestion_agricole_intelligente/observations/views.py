from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .forms import ObservationForm
from .models import Observation
from services.observation_service import ObservationService


@login_required
def liste_observations(request):
    resultat = ObservationService.lister_observations(request.user, request.GET)

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "observations/liste.html",
        {
            "observations": resultat["observations"],
            "page_obj": resultat["page_obj"],
            "total": resultat["total"],
            "filtres": resultat["filtres"],
            "query_params": query_params.urlencode(),
        },
    )


@login_required
def ajouter_observation(request):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seule l'agricultrice ou l'agriculteur peut créer une observation.")

    formulaire = ObservationForm(utilisateur=request.user)

    if request.method == "POST":
        formulaire = ObservationForm(request.POST, request.FILES, utilisateur=request.user)
        if formulaire.is_valid():
            ObservationService.creer_observation(request.user, formulaire)
            messages.success(request, "Observation ajoutée.")
            return redirect("observations:liste")

    return render(request, "observations/ajouter.html", {"form": formulaire})


@login_required
def consulter_observation(request, pk):
    try:
        observation = ObservationService.obtenir_observation(request.user, pk)
    except Observation.DoesNotExist:
        raise Http404("Observation non trouvée")
    except PermissionDenied:
        raise PermissionDenied

    return render(request, "observations/detail.html", {"observation": observation})


@login_required
def modifier_observation(request, pk):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seule l'agricultrice ou l'agriculteur peut modifier une observation.")

    try:
        observation = ObservationService.obtenir_observation(request.user, pk)
    except Observation.DoesNotExist:
        raise Http404("Observation non trouvée")
    except PermissionDenied:
        raise PermissionDenied

    formulaire = ObservationForm(request.POST or None, request.FILES or None, instance=observation, utilisateur=request.user)

    if request.method == "POST" and formulaire.is_valid():
        ObservationService.modifier_observation(request.user, observation, formulaire)
        messages.success(request, "Observation modifiée.")
        return redirect(reverse("observations:detail", args=[observation.pk]))

    return render(request, "observations/modifier.html", {"form": formulaire, "observation": observation})


@login_required
def supprimer_observation(request, pk):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seule l'agricultrice ou l'agriculteur peut supprimer une observation.")

    try:
        observation = ObservationService.obtenir_observation(request.user, pk)
    except Observation.DoesNotExist:
        raise Http404("Observation non trouvée")
    except PermissionDenied:
        raise PermissionDenied

    if request.method == "POST":
        ObservationService.supprimer_observation(request.user, observation)
        messages.success(request, "Observation supprimée.")
        return redirect("observations:liste")

    return render(request, "observations/supprimer.html", {"observation": observation})

# Create your views here.
