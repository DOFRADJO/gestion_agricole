from django.utils import timezone

from utilisateurs.models import Utilisateur, Agriculteur, Agronome
from cultures.models import Culture
from observations.models import Observation
from predictions.models import Prediction


class DashboardService:
    """
    Fournit les métriques et données pour les tableaux de bord.
    """

    @staticmethod
    def obtenir_dashboard(utilisateur):
        type_utilisateur = utilisateur.get_type_utilisateur()

        if type_utilisateur == "administrateur":
            return DashboardService._dashboard_administrateur()

        if type_utilisateur == "agronome":
            return DashboardService._dashboard_agronome()

        if type_utilisateur == "agriculteur":
            return DashboardService._dashboard_agriculteur(utilisateur)

        return {
            "dashboard_title": "Tableau de bord",
            "statistiques": [],
            "activites_recents": [],
            "quick_actions": [],
            "now": timezone.now(),
        }

    @staticmethod
    def _dashboard_administrateur():
        statistiques = [
            {
                "label": "Cultures",
                "value": Culture.objects.count(),
                "icon": "bi-seedling",
                "variant": "primary",
            },
            {
                "label": "Agriculteurs",
                "value": Agriculteur.objects.count(),
                "icon": "bi-people",
                "variant": "success",
            },
            {
                "label": "Agronomes",
                "value": Agronome.objects.count(),
                "icon": "bi-person-badge",
                "variant": "info",
            },
            {
                "label": "Observations",
                "value": Observation.objects.count(),
                "icon": "bi-eye",
                "variant": "secondary",
            },
            {
                "label": "Prédictions",
                "value": Prediction.objects.count(),
                "icon": "bi-bar-chart-line",
                "variant": "warning",
            },
            {
                "label": "Recommandations",
                "value": 0,
                "icon": "bi-lightbulb",
                "variant": "danger",
            },
        ]
        activites_recents = [
            {
                "title": f"{culture.nom} semé",
                "description": f"{culture.agriculteur.get_full_name} — {culture.localisation.title()}",
                "date": culture.date_semis,
            }
            for culture in Culture.objects.select_related("agriculteur").order_by("-date_semis")[:5]
        ]
        quick_actions = [
            {"label": "Voir toutes les cultures", "url": "/cultures/", "icon": "bi-seedling"},
            {"label": "Explorer les prédictions", "url": "/predictions/", "icon": "bi-bar-chart-line"},
            {"label": "Accéder à l'administration", "url": "/admin/", "icon": "bi-gear"},
        ]

        return {
            "dashboard_title": "Tableau de bord administrateur",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
            "now": timezone.now(),
        }

    @staticmethod
    def _dashboard_agronome():
        statistiques = [
            {
                "label": "Cultures suivies",
                "value": Culture.objects.count(),
                "icon": "bi-seedling",
                "variant": "primary",
            },
            {
                "label": "Agriculteurs",
                "value": Agriculteur.objects.count(),
                "icon": "bi-people",
                "variant": "success",
            },
            {
                "label": "Observations",
                "value": Observation.objects.count(),
                "icon": "bi-eye",
                "variant": "secondary",
            },
            {
                "label": "Prédictions",
                "value": Prediction.objects.count(),
                "icon": "bi-bar-chart-line",
                "variant": "warning",
            },
        ]
        activites_recents = [
            {
                "title": f"{culture.nom} semé",
                "description": f"{culture.agriculteur.get_full_name} — {culture.localisation.title()}",
                "date": culture.date_semis,
            }
            for culture in Culture.objects.select_related("agriculteur").order_by("-date_semis")[:5]
        ]
        quick_actions = [
            {"label": "Explorer les cultures", "url": "/cultures/", "icon": "bi-seedling"},
            {"label": "Voir les prédictions", "url": "/predictions/", "icon": "bi-bar-chart-line"},
        ]

        return {
            "dashboard_title": "Tableau de bord agronome",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
            "now": timezone.now(),
        }

    @staticmethod
    def _dashboard_agriculteur(utilisateur):
        propres_cultures = Culture.objects.filter(agriculteur=utilisateur.agriculteur)
        statistiques = [
            {
                "label": "Mes cultures",
                "value": propres_cultures.count(),
                "icon": "bi-seedling",
                "variant": "primary",
            },
            {
                "label": "Prédictions",
                "value": Prediction.objects.filter(culture__agriculteur=utilisateur.agriculteur).count(),
                "icon": "bi-bar-chart-line",
                "variant": "warning",
            },
            {
                "label": "Recommandations",
                "value": 0,
                "icon": "bi-lightbulb",
                "variant": "success",
            },
        ]
        activites_recents = [
            {
                "title": f"{culture.nom} semé",
                "description": f"{culture.localisation.title()}",
                "date": culture.date_semis,
            }
            for culture in propres_cultures.order_by("-date_semis")[:5]
        ]
        quick_actions = [
            {"label": "Ajouter une culture", "url": "/cultures/ajouter/", "icon": "bi-plus-lg"},
            {"label": "Voir mes cultures", "url": "/cultures/", "icon": "bi-list-ul"},
            {"label": "Voir mes prédictions", "url": "/predictions/", "icon": "bi-bar-chart-line"},
        ]

        return {
            "dashboard_title": "Tableau de bord agriculteur",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
            "now": timezone.now(),
        }
