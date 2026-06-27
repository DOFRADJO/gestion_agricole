from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from observations.models import Observation
from cultures.models import Culture


class ObservationService:
    """
    Service pour la gestion des observations.
    """

    @staticmethod
    def creer_observation(utilisateur, formulaire):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut créer une observation.")

        observation = formulaire.save(commit=False)
        if observation.culture.agriculteur != utilisateur.agriculteur:
            raise PermissionDenied("L'observation doit appartenir à une culture de l'agriculteur.")

        observation.full_clean()
        observation.save()
        return observation

    @staticmethod
    def modifier_observation(utilisateur, observation, formulaire):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut modifier une observation.")

        if observation.culture.agriculteur != utilisateur.agriculteur:
            raise PermissionDenied("Accès refusé à cette observation.")

        obs = formulaire.save(commit=False)
        obs.pk = observation.pk
        obs.full_clean()
        obs.save()
        return obs

    @staticmethod
    def supprimer_observation(utilisateur, observation):
        if utilisateur.get_type_utilisateur() != "agriculteur":
            raise PermissionDenied("Seul l'agriculteur peut supprimer une observation.")

        if observation.culture.agriculteur != utilisateur.agriculteur:
            raise PermissionDenied("Accès refusé à cette observation.")

        observation.delete()

    @staticmethod
    def obtenir_observation(utilisateur, pk):
        try:
            observation = Observation.objects.select_related("culture").get(pk=pk)
        except Observation.DoesNotExist:
            raise
        type_user = utilisateur.get_type_utilisateur()
        if type_user == "agriculteur":
            if observation.culture.agriculteur != utilisateur.agriculteur:
                raise PermissionDenied
        return observation

    @staticmethod
    def lister_observations(utilisateur, params):
        qs = Observation.objects.select_related("culture").order_by("-date_observation")

        if utilisateur.get_type_utilisateur() == "agriculteur":
            qs = qs.filter(culture__agriculteur=utilisateur.agriculteur)

        # filters: culture and date range
        culture_id = params.get("culture")
        if culture_id:
            qs = qs.filter(culture_id=culture_id)

        date_debut = params.get("date_debut")
        if date_debut:
            qs = qs.filter(date_observation__gte=date_debut)

        date_fin = params.get("date_fin")
        if date_fin:
            qs = qs.filter(date_observation__lte=date_fin)

        # simple pagination
        paginator = Paginator(qs, 10)
        page_number = params.get("page") or 1
        page_obj = paginator.get_page(page_number)

        return {
            "observations": page_obj.object_list,
            "page_obj": page_obj,
            "total": paginator.count,
            "filtres": {"culture": culture_id, "date_debut": date_debut, "date_fin": date_fin},
        }
