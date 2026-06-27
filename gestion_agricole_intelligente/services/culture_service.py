from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404
from django.db.models import Q

from cultures.models import Culture
from utilisateurs.models import Agriculteur


class CultureService:
    """
    Service responsable de la gestion métier des cultures.
    """

    FILTRES = {
        "nom": "nom__icontains",
        "localisation": "localisation__icontains",
        "statut": "statut__icontains",
    }

    TRI_AUTORISE = {
        "nom": "nom",
        "superficie": "superficie",
        "date_semis": "date_semis",
        "localisation": "localisation",
        "statut": "statut",
    }

    @staticmethod
    def _parse_date(valeur):
        try:
            return datetime.strptime(valeur, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def creer_culture(utilisateur, formulaire):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut créer une culture.")

        culture = formulaire.save(commit=False)
        culture.agriculteur = utilisateur.agriculteur
        culture.full_clean()
        culture.save()
        return culture

    @staticmethod
    def obtenir_cultures(utilisateur, params=None):
        params = params or {}
        cultures = Culture.objects.select_related("agriculteur").all()

        type_utilisateur = utilisateur.get_type_utilisateur()
        if type_utilisateur == "agriculteur":
            cultures = cultures.filter(agriculteur=utilisateur.agriculteur)

        recherche = params.get("q", "").strip()
        localisation = params.get("localisation", "").strip()
        date_debut = CultureService._parse_date(params.get("date_debut"))
        date_fin = CultureService._parse_date(params.get("date_fin"))

        if recherche:
            cultures = cultures.filter(
                Q(nom__icontains=recherche)
                | Q(localisation__icontains=recherche)
                | Q(statut__icontains=recherche)
            )

        if localisation:
            cultures = cultures.filter(localisation__icontains=localisation)

        if date_debut:
            cultures = cultures.filter(date_semis__gte=date_debut)

        if date_fin:
            cultures = cultures.filter(date_semis__lte=date_fin)

        tri = params.get("sort", "date_semis")
        ordre = params.get("order", "desc")
        champ_tri = CultureService.TRI_AUTORISE.get(tri, "date_semis")

        if ordre == "asc":
            cultures = cultures.order_by(champ_tri)
        else:
            cultures = cultures.order_by(f"-{champ_tri}")

        paginator = Paginator(cultures, 10)
        page_obj = paginator.get_page(params.get("page"))

        return {
            "cultures": page_obj.object_list,
            "page_obj": page_obj,
            "total": paginator.count,
            "recherche": recherche,
            "localisation": localisation,
            "date_debut": date_debut,
            "date_fin": date_fin,
            "tri": tri,
            "ordre": ordre,
        }

    @staticmethod
    def obtenir_culture(utilisateur, pk):
        culture = Culture.objects.select_related("agriculteur").get(pk=pk)

        if (
            utilisateur.get_type_utilisateur() == "agriculteur"
            and culture.agriculteur != utilisateur.agriculteur
        ):
            raise PermissionDenied("Accès refusé à cette culture.")

        return culture

    @staticmethod
    def modifier_culture(utilisateur, culture, formulaire):
        type_utilisateur = utilisateur.get_type_utilisateur()

        if type_utilisateur != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut modifier une culture.")

        if culture.agriculteur != utilisateur.agriculteur:
            raise PermissionDenied("Accès refusé à cette culture.")

        culture_modifiee = formulaire.save(commit=False)
        culture_modifiee.agriculteur = utilisateur.agriculteur
        culture_modifiee.pk = culture.pk
        culture_modifiee.full_clean()
        culture_modifiee.save()

        return culture_modifiee

    @staticmethod
    def supprimer_culture(utilisateur, culture):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut supprimer une culture.")

        if culture.agriculteur != utilisateur.agriculteur:
            raise PermissionDenied("Accès refusé à cette culture.")

        culture.delete()

    @staticmethod
    def obtenir_agriculteurs():
        return Agriculteur.objects.order_by("first_name", "last_name")
