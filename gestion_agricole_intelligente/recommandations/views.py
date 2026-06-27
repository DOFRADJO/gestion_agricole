from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from recommandations.models import Recommandation
from services.recommandation_service import RecommendationService


@login_required
def liste_recommandations(request):
    recommandations = RecommendationService.obtenir_recommandations(request.user)
    return render(
        request,
        "recommandations/liste.html",
        {"recommandations": recommandations},
    )


@login_required
def detail_recommandation(request, pk):
    recommandation = get_object_or_404(
        Recommandation.objects.select_related("culture", "culture__agriculteur"),
        pk=pk,
    )

    if (
        request.user.get_type_utilisateur() == "agriculteur"
        and recommandation.culture.agriculteur != request.user.agriculteur
    ):
        raise PermissionDenied

    return render(
        request,
        "recommandations/detail.html",
        {"recommandation": recommandation},
    )


@login_required
def historique_recommandations(request):
    historique = RecommendationService.historique(request.user)
    return render(
        request,
        "recommandations/historique.html",
        {"historique": historique},
    )
