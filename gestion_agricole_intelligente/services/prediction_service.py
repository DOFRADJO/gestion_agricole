from django.core.exceptions import PermissionDenied
from django.utils import timezone

from cultures.models import Culture
from observations.models import Observation
from predictions.models import Prediction


class PredictionService:
    """
    Service responsable de la génération et de l'accès aux prédictions.
    """

    @staticmethod
    def _calculer_prediction(culture: Culture) -> tuple[float, float, str]:
        observations = list(culture.observations.order_by("-date_observation"))
        age_jours = culture.age_en_jours()

        if not observations:
            rendement = round(max(0.0, 1.0 + min(age_jours, 90) * 0.02), 2)
            confiance = 0.20
            commentaires = "Prédiction provisoire générée sans observation."
        else:
            nombre_obs = len(observations)
            rendement = round(2.0 + min(nombre_obs, 12) * 0.25 + min(age_jours, 120) * 0.015, 2)
            confiance = min(1.0, 0.35 + min(nombre_obs, 12) * 0.05 + min(age_jours, 120) * 0.008)
            commentaires = (
                f"Basé sur {nombre_obs} observation(s) et l'âge de la culture ({age_jours} jours)."
            )

        return rendement, confiance, commentaires

    @staticmethod
    def generer_prediction(culture: Culture) -> Prediction:
        """
        Génère ou met à jour la prédiction pour une culture.

        La logique est provisoire : elle s'appuie sur le nombre d'observations
        et l'âge de la culture pour produire un rendement estimé et un niveau de confiance.
        """
        if not isinstance(culture, Culture):
            raise ValueError("culture doit être une instance de Culture")

        rendement, confiance, commentaires = PredictionService._calculer_prediction(culture)
        date_prediction = timezone.localdate()

        prediction = Prediction.objects.filter(culture=culture, datePrediction=date_prediction).first()
        if prediction is None:
            prediction = Prediction(
                culture=culture,
                datePrediction=date_prediction,
                rendementEstime=rendement,
                niveauConfiance=confiance,
                commentaires=commentaires,
            )
        else:
            prediction.rendementEstime = rendement
            prediction.niveauConfiance = confiance
            prediction.commentaires = commentaires

        prediction.full_clean()
        prediction.save()
        return prediction

    @staticmethod
    def obtenir_prediction(culture: Culture) -> Prediction:
        """
        Retourne la prédiction la plus récente pour une culture.

        Si aucune prédiction n'existe, elle est générée automatiquement.
        """
        prediction = Prediction.objects.filter(culture=culture).order_by("-datePrediction", "-id").first()
        if prediction is None:
            prediction = PredictionService.generer_prediction(culture)
        return prediction

    @staticmethod
    def obtenir_predictions_agriculteur(utilisateur):
        """
        Retourne les prédictions actuelles pour toutes les cultures de l'agriculteur.
        """
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul un agriculteur peut obtenir ses prédictions personnelles.")

        predictions = []
        for culture in Culture.objects.filter(agriculteur=utilisateur.agriculteur):
            predictions.append(PredictionService.obtenir_prediction(culture))
        return predictions

    @staticmethod
    def obtenir_predictions(utilisateur):
        """
        Retourne les prédictions accessibles à l'utilisateur.
        """
        type_user = utilisateur.get_type_utilisateur()
        if type_user == "agriculteur":
            return PredictionService.obtenir_predictions_agriculteur(utilisateur)

        for culture in Culture.objects.all():
            PredictionService.obtenir_prediction(culture)

        return Prediction.objects.select_related("culture", "culture__agriculteur").order_by("-datePrediction", "-id")

    @staticmethod
    def recalculer_prediction(culture: Culture) -> Prediction:
        """
        Recalcule la prédiction pour une culture lorsqu'une nouvelle observation est disponible.
        """
        return PredictionService.generer_prediction(culture)

    @staticmethod
    def historique(utilisateur, culture=None):
        """
        Retourne l'historique des prédictions accessibles à l'utilisateur.
        """
        qs = Prediction.objects.select_related("culture", "culture__agriculteur").order_by("-datePrediction", "-id")

        type_user = utilisateur.get_type_utilisateur()
        if type_user == "agriculteur":
            qs = qs.filter(culture__agriculteur=utilisateur.agriculteur)

        if culture is not None:
            qs = qs.filter(culture=culture)

        return qs
