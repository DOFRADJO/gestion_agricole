from django.core.exceptions import PermissionDenied
from django.utils import timezone

from cultures.models import Culture
from recommandations.models import Recommandation


class RecommendationService:
    """
    Service responsable de la génération et de l'accès aux recommandations agronomiques.

    La logique actuelle est provisoire et peut être remplacée ultérieurement par un moteur IA.
    """

    @staticmethod
    def _calculer_recommandation(prediction):
        if prediction is None:
            raise ValueError("prediction ne peut pas être None")

        rendement = prediction.rendementEstime
        confiance = prediction.niveauConfiance

        if rendement < 2.5:
            type_recommandation = "Faible rendement"
            contenu = (
                "Appliquer un apport d'engrais adapté, renforcer l'irrigation et surveiller les maladies."
            )
        elif rendement < 4.0:
            type_recommandation = "Rendement moyen"
            contenu = (
                "Maintenir les bonnes pratiques culturales et surveiller l'évolution des observations."
            )
        else:
            type_recommandation = "Rendement élevé"
            contenu = (
                "Poursuivre les pratiques actuelles et préparer la récolte tout en surveillant la vigne."
            )

        if confiance < 0.5:
            contenu += " Le niveau de confiance est faible ; complétez les observations pour affiner la recommandation."

        return type_recommandation, contenu

    @staticmethod
    def generer_recommandation(culture: Culture) -> Recommandation:
        from services.prediction_service import PredictionService

        prediction = PredictionService.obtenir_prediction(culture)
        type_recommandation, contenu = RecommendationService._calculer_recommandation(prediction)
        date_recommandation = timezone.localdate()

        recommandation = Recommandation.objects.filter(
            culture=culture,
            dateRecommandation=date_recommandation,
        ).first()

        if recommandation is None:
            recommandation = Recommandation(
                culture=culture,
                dateRecommandation=date_recommandation,
                type=type_recommandation,
                contenu=contenu,
            )
        else:
            recommandation.type = type_recommandation
            recommandation.contenu = contenu

        recommandation.full_clean()
        recommandation.save()
        return recommandation

    @staticmethod
    def obtenir_recommandation(culture: Culture) -> Recommandation:
        recommandation = Recommandation.objects.filter(culture=culture).order_by(
            "-dateRecommandation", "-id"
        ).first()
        if recommandation is None:
            recommandation = RecommendationService.generer_recommandation(culture)
        return recommandation

    @staticmethod
    def obtenir_recommandations_agriculteur(utilisateur):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul un agriculteur peut accéder à ses recommandations.")

        cultures = Culture.objects.filter(agriculteur=utilisateur.agriculteur)
        for culture in cultures:
            RecommendationService.obtenir_recommandation(culture)

        return Recommandation.objects.select_related("culture", "culture__agriculteur").filter(
            culture__agriculteur=utilisateur.agriculteur
        ).order_by("-dateRecommandation", "-id")

    @staticmethod
    def obtenir_recommandations(utilisateur):
        type_user = utilisateur.get_type_utilisateur()

        if type_user == "agriculteur":
            return RecommendationService.obtenir_recommandations_agriculteur(utilisateur)

        cultures = Culture.objects.select_related("agriculteur").all()
        for culture in cultures:
            RecommendationService.obtenir_recommandation(culture)

        return Recommandation.objects.select_related("culture", "culture__agriculteur").order_by(
            "-dateRecommandation", "-id"
        )

    @staticmethod
    def mettre_a_jour_recommandation(culture: Culture) -> Recommandation:
        return RecommendationService.generer_recommandation(culture)

    @staticmethod
    def historique(utilisateur, culture=None):
        qs = Recommandation.objects.select_related("culture", "culture__agriculteur").order_by(
            "-dateRecommandation", "-id"
        )
        if utilisateur.get_type_utilisateur() == "agriculteur":
            qs = qs.filter(culture__agriculteur=utilisateur.agriculteur)

        if culture is not None:
            qs = qs.filter(culture=culture)

        return qs
