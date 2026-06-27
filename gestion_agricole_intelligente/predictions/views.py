from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from predictions.models import Prediction
from services.prediction_service import PredictionService


@login_required
def liste_predictions(request):
    predictions = PredictionService.obtenir_predictions(request.user)
    return render(
        request,
        "predictions/liste.html",
        {
            "predictions": predictions,
        },
    )


@login_required
def detail_prediction(request, pk):
    prediction = get_object_or_404(
        Prediction.objects.select_related("culture", "culture__agriculteur"),
        pk=pk,
    )

    if (
        request.user.get_type_utilisateur() == "agriculteur"
        and prediction.culture.agriculteur != request.user.agriculteur
    ):
        raise PermissionDenied

    return render(
        request,
        "predictions/detail.html",
        {
            "prediction": prediction,
        },
    )


@login_required
def historique_predictions(request):
    historique = PredictionService.historique(request.user)
    return render(
        request,
        "predictions/historique.html",
        {
            "historique": historique,
        },
    )
