from django.contrib.auth.models import Group

from utilisateurs.models import (
    Administrateur,
    Agriculteur,
    Agronome,
    Utilisateur,
)


class UtilisateurService:
    """
    Service responsable de la gestion des utilisateurs.
    """

    @staticmethod
    def obtenir_type(utilisateur):
        if Administrateur.objects.filter(pk=utilisateur.pk).exists():
            return "administrateur"

        if Agronome.objects.filter(pk=utilisateur.pk).exists():
            return "agronome"

        if Agriculteur.objects.filter(pk=utilisateur.pk).exists():
            return "agriculteur"

        return "utilisateur"

    @staticmethod
    def _extraire_champs_parent(utilisateur: Utilisateur):
        champs = {}

        for field in utilisateur._meta.fields:
            if field.primary_key:
                continue
            champs[field.name] = getattr(utilisateur, field.name)

        return champs

    @staticmethod
    def _creer_sous_classe(utilisateur: Utilisateur, sous_classe):
        instance = sous_classe.objects.filter(pk=utilisateur.pk).first()
        if instance:
            return instance

        attributs = UtilisateurService._extraire_champs_parent(utilisateur)
        instance = sous_classe(pk=utilisateur.pk, **attributs)
        instance.save(force_insert=False)
        return instance

    @staticmethod
    def ajouter_groupe(utilisateur, nom_groupe):
        groupe, _ = Group.objects.get_or_create(name=nom_groupe)
        utilisateur.groups.add(groupe)

    @staticmethod
    def creer_agriculteur(utilisateur: Utilisateur):

        agriculteur = UtilisateurService._creer_sous_classe(
            utilisateur,
            Agriculteur,
        )

        UtilisateurService.ajouter_groupe(
            utilisateur,
            "Agriculteurs",
        )

        return agriculteur

    @staticmethod
    def creer_agronome(utilisateur: Utilisateur):

        agronome = UtilisateurService._creer_sous_classe(
            utilisateur,
            Agronome,
        )

        UtilisateurService.ajouter_groupe(
            utilisateur,
            "Agronomes",
        )

        return agronome

    @staticmethod
    def creer_administrateur(utilisateur: Utilisateur):

        administrateur = UtilisateurService._creer_sous_classe(
            utilisateur,
            Administrateur,
        )

        UtilisateurService.ajouter_groupe(
            utilisateur,
            "Administrateurs",
        )

        return administrateur