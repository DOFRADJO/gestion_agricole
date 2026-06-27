from django.utils import timezone

from utilisateurs.models import Utilisateur
from cultures.models import Culture


class DashboardService:
    """
    Fournit les métriques et données pour les tableaux de bord.
    """

    @staticmethod
    def obtenir_dashboard(utilisateur):
        # Counts
        total_cultures = Culture.objects.count()
        total_agriculteurs = Utilisateur.objects.filter(
            agriculteur__isnull=False
        ).count()
        total_agronomes = Utilisateur.objects.filter(
            agronome__isnull=False
        ).count()
        total_administrateurs = Utilisateur.objects.filter(
            administrateur__isnull=False
        ).count()

        # Placeholder counts for other modules (may be implemented later)
        total_observations = 0
        total_predictions = 0
        total_recommandations = 0

        # Recent activities: last 5 cultures created
        recent_cultures = Culture.objects.select_related("agriculteur").order_by("-date_creation")[:5]

        contexte = {
            "total_cultures": total_cultures,
            "total_agriculteurs": total_agriculteurs,
            "total_agronomes": total_agronomes,
            "total_administrateurs": total_administrateurs,
            "total_observations": total_observations,
            "total_predictions": total_predictions,
            "total_recommandations": total_recommandations,
            "recent_cultures": recent_cultures,
            "now": timezone.now(),
        }

        return contexte
from cultures.models import Culture
from utilisateurs.models import Agriculteur, Agronome


class DashboardService:
    """
    Service responsable des données des tableaux de bord.
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
                "value": 0,
                "icon": "bi-eye",
                "variant": "secondary",
            },
            {
                "label": "Prédictions",
                "value": 0,
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
                "title": f"{culture.nom} mis à jour",
                "description": f"{culture.agriculteur.get_full_name} — {culture.localisation.title()}",
                "date": culture.date_modification,
            }
            for culture in Culture.objects.select_related("agriculteur").order_by("-date_modification")[:5]
        ]
        quick_actions = [
            {"label": "Voir toutes les cultures", "url": "/cultures/", "icon": "bi-seedling"},
            {"label": "Accéder à l'administration", "url": "/admin/", "icon": "bi-gear"},
        ]

        return {
            "dashboard_title": "Tableau de bord administrateur",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
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
                "value": 0,
                "icon": "bi-eye",
                "variant": "secondary",
            },
        ]
        activites_recents = [
            {
                "title": f"{culture.nom} mise à jour",
                "description": f"{culture.agriculteur.get_full_name} — {culture.localisation.title()}",
                "date": culture.date_modification,
            }
            for culture in Culture.objects.select_related("agriculteur").order_by("-date_modification")[:5]
        ]
        quick_actions = [
            {"label": "Explorer les cultures", "url": "/cultures/", "icon": "bi-seedling"},
        ]

        return {
            "dashboard_title": "Tableau de bord agronome",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
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
                "label": "Rendements",
                "value": 0,
                "icon": "bi-bar-chart-line",
                "variant": "info",
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
                "title": f"{culture.nom} mise à jour",
                "description": f"{culture.localisation.title()}",
                "date": culture.date_modification,
            }
            for culture in propres_cultures.order_by("-date_modification")[:5]
        ]
        quick_actions = [
            {"label": "Ajouter une culture", "url": "/cultures/ajouter/", "icon": "bi-plus-lg"},
            {"label": "Voir mes cultures", "url": "/cultures/", "icon": "bi-list-ul"},
        ]

        return {
            "dashboard_title": "Tableau de bord agriculteur",
            "statistiques": statistiques,
            "activites_recents": activites_recents,
            "quick_actions": quick_actions,
        }
