"""Service de gestion des utilisateurs et des profils.

Ce module contient l'ensemble de la logique métier de l'administrateur pour
la création, modification, suppression et filtrage des utilisateurs. Il reste
conforme à l'architecture Vue → Service → Modèle du projet.
"""

from django.contrib.auth.models import Group
from django.db.models import Q

from utilisateurs.models import (
    Administrateur,
    Agriculteur,
    Agronome,
    Utilisateur,
)


TYPE_UTILISATEUR_GROUPES = {
    "administrateur": "Administrateurs",
    "agronome": "Agronomes",
    "agriculteur": "Agriculteurs",
}


class UtilisateurService:
    """Service responsable de la gestion fonctionnelle des utilisateurs."""

    @staticmethod
    def obtenir_type(utilisateur):
        """Retourne le type de profil utilisateur réel.

        Le type est déduit à partir de la présence d'une ligne de sous-classe
        `Administrateur`, `Agronome` ou `Agriculteur`.
        """
        if Administrateur.objects.filter(pk=utilisateur.pk).exists():
            return "administrateur"

        if Agronome.objects.filter(pk=utilisateur.pk).exists():
            return "agronome"

        if Agriculteur.objects.filter(pk=utilisateur.pk).exists():
            return "agriculteur"

        return "utilisateur"

    @staticmethod
    def _extraire_champs_parent(utilisateur: Utilisateur):
        """Extrait les champs hérités du modèle parent `Utilisateur`."""
        champs = {}

        for field in utilisateur._meta.fields:
            if field.primary_key:
                continue
            champs[field.name] = getattr(utilisateur, field.name)

        return champs

    @staticmethod
    def _creer_sous_classe(utilisateur: Utilisateur, sous_classe):
        """Crée la ligne de sous-classe liée à un utilisateur existant.

        Si le profil existe déjà, il est renvoyé tel quel.
        """
        instance = sous_classe.objects.filter(pk=utilisateur.pk).first()
        if instance:
            return instance

        attributs = UtilisateurService._extraire_champs_parent(utilisateur)
        instance = sous_classe(pk=utilisateur.pk, **attributs)
        instance.save(force_insert=False)
        return instance

    @staticmethod
    def _supprimer_profils(utilisateur: Utilisateur):
        """Supprime toutes les lignes de profil liées à l'utilisateur."""
        Administrateur.objects.filter(pk=utilisateur.pk).delete()
        Agronome.objects.filter(pk=utilisateur.pk).delete()
        Agriculteur.objects.filter(pk=utilisateur.pk).delete()

    @staticmethod
    def _supprimer_groupes_de_profil(utilisateur: Utilisateur):
        """Retire l'utilisateur des groupes de profils définis."""
        groupes = Group.objects.filter(name__in=TYPE_UTILISATEUR_GROUPES.values())
        utilisateur.groups.remove(*groupes)

    @staticmethod
    def _changer_type(utilisateur: Utilisateur, type_utilisateur: str):
        """Change le type de profil d'un utilisateur en conservant ses données."""
        UtilisateurService._supprimer_profils(utilisateur)
        UtilisateurService._supprimer_groupes_de_profil(utilisateur)

        if type_utilisateur == "administrateur":
            utilisateur.is_staff = True
            utilisateur.save()
            UtilisateurService.creer_administrateur(utilisateur)
            return

        if type_utilisateur == "agronome":
            utilisateur.is_staff = False
            utilisateur.is_superuser = False
            utilisateur.save()
            UtilisateurService.creer_agronome(utilisateur)
            return

        if type_utilisateur == "agriculteur":
            utilisateur.is_staff = False
            utilisateur.is_superuser = False
            utilisateur.save()
            UtilisateurService.creer_agriculteur(utilisateur)
            return

    @staticmethod
    def obtenir_utilisateurs(parametres):
        """Retourne la liste des utilisateurs filtrés selon les paramètres.

        Arguments:
            parametres: dictionnaire de paramètres GET contenant `q`, `type` et `actif`.

        Retourne un dictionnaire avec les utilisateurs et les valeurs de filtre.
        """
        utilisateurs = Utilisateur.objects.order_by("last_name", "first_name")
        recherche = parametres.get("q", "").strip()
        type_utilisateur = parametres.get("type", "").strip()
        actif = parametres.get("actif", "").strip()

        if recherche:
            utilisateurs = utilisateurs.filter(
                Q(email__icontains=recherche)
                | Q(username__icontains=recherche)
                | Q(first_name__icontains=recherche)
                | Q(last_name__icontains=recherche)
            )

        if type_utilisateur == "administrateur":
            utilisateurs = utilisateurs.filter(pk__in=Administrateur.objects.values_list("pk", flat=True))
        elif type_utilisateur == "agronome":
            utilisateurs = utilisateurs.filter(pk__in=Agronome.objects.values_list("pk", flat=True))
        elif type_utilisateur == "agriculteur":
            utilisateurs = utilisateurs.filter(pk__in=Agriculteur.objects.values_list("pk", flat=True))
        elif type_utilisateur == "utilisateur":
            utilisateurs = utilisateurs.exclude(pk__in=Administrateur.objects.values_list("pk", flat=True))
            utilisateurs = utilisateurs.exclude(pk__in=Agronome.objects.values_list("pk", flat=True))
            utilisateurs = utilisateurs.exclude(pk__in=Agriculteur.objects.values_list("pk", flat=True))

        if actif == "1":
            utilisateurs = utilisateurs.filter(is_active=True)
        elif actif == "0":
            utilisateurs = utilisateurs.filter(is_active=False)

        return {
            "utilisateurs": utilisateurs,
            "recherche": recherche,
            "type_utilisateur": type_utilisateur,
            "actif": actif,
        }

    @staticmethod
    def creer_utilisateur(formulaire):
        data = formulaire.cleaned_data
        utilisateur = Utilisateur.objects.create_user(
            email=data["email"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["mot_de_passe"],
            is_active=data["is_active"],
            is_staff=data["type_utilisateur"] == "administrateur",
        )

        UtilisateurService._changer_type(utilisateur, data["type_utilisateur"])
        return utilisateur

    @staticmethod
    def modifier_utilisateur(formulaire, utilisateur: Utilisateur):
        data = formulaire.cleaned_data
        utilisateur.email = data["email"]
        utilisateur.username = data["username"]
        utilisateur.first_name = data["first_name"]
        utilisateur.last_name = data["last_name"]
        utilisateur.is_active = data["is_active"]
        utilisateur.is_staff = data["type_utilisateur"] == "administrateur"

        if data.get("mot_de_passe"):
            utilisateur.set_password(data["mot_de_passe"])

        if data["type_utilisateur"] != "administrateur":
            utilisateur.is_superuser = False

        utilisateur.save()
        UtilisateurService._changer_type(utilisateur, data["type_utilisateur"])
        return utilisateur

    @staticmethod
    def supprimer_utilisateur(utilisateur: Utilisateur):
        utilisateur.delete()

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