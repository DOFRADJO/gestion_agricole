from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .forms import CultureForm
from .models import Culture
from services.culture_service import CultureService


@login_required
def liste_cultures(request):
    resultat = CultureService.obtenir_cultures(
        request.user,
        request.GET,
    )

    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "cultures/liste.html",
        {
            "cultures": resultat["cultures"],
            "page_obj": resultat["page_obj"],
            "total": resultat["total"],
            "recherche": resultat["recherche"],
            "localisation": resultat["localisation"],
            "date_debut": resultat["date_debut"],
            "date_fin": resultat["date_fin"],
            "tri": resultat["tri"],
            "ordre": resultat["ordre"],
            "query_params": query_params.urlencode(),
        },
    )


@login_required
def ajouter_culture(request):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seul l'agriculteur peut créer une culture.")

    formulaire = CultureForm(utilisateur=request.user)

    if request.method == "POST":
        formulaire = CultureForm(
            request.POST,
            utilisateur=request.user,
        )

        if formulaire.is_valid():
            CultureService.creer_culture(
                request.user,
                formulaire,
            )
            messages.success(request, "La culture a été ajoutée avec succès.")
            return redirect("cultures:liste")

    return render(
        request,
        "cultures/ajouter.html",
        {
            "form": formulaire,
        },
    )


@login_required
def consulter_culture(request, pk):
    try:
        culture = CultureService.obtenir_culture(request.user, pk)
    except Culture.DoesNotExist:
        raise Http404("Culture non trouvée")
    except PermissionDenied:
        raise PermissionDenied

    return render(request, "cultures/detail.html", {"culture": culture})


@login_required
def modifier_culture(request, pk):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seul l'agriculteur peut modifier une culture.")

    try:
        culture = CultureService.obtenir_culture(request.user, pk)
    except Culture.DoesNotExist:
        raise Http404("Culture non trouvée")
    except PermissionDenied:
        raise PermissionDenied
    formulaire = CultureForm(
        request.POST or None,
        instance=culture,
        utilisateur=request.user,
    )

    if request.method == "POST" and formulaire.is_valid():
        CultureService.modifier_culture(
            request.user,
            culture,
            formulaire,
        )
        messages.success(request, "La culture a été modifiée avec succès.")
        return redirect(
            reverse("cultures:detail", args=[culture.pk])
        )

    return render(
        request,
        "cultures/modifier.html",
        {
            "form": formulaire,
            "culture": culture,
        },
    )


@login_required
def supprimer_culture(request, pk):
    if request.user.get_type_utilisateur() != "agriculteur":
        raise PermissionDenied("Seul l'agriculteur peut supprimer une culture.")

    try:
        culture = CultureService.obtenir_culture(request.user, pk)
    except Culture.DoesNotExist:
        raise Http404("Culture non trouvée")
    except PermissionDenied:
        raise PermissionDenied

    if request.method == "POST":
        CultureService.supprimer_culture(request.user, culture)
        messages.success(request, "La culture a été supprimée avec succès.")
        return redirect("cultures:liste")

    return render(request, "cultures/supprimer.html", {"culture": culture})