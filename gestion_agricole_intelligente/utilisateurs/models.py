from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UtilisateurManager


class Utilisateur(AbstractUser):
    """
    Classe mère représentant tous les utilisateurs du système.
    """

    email = models.EmailField(
        unique=True,
        verbose_name="Adresse e-mail",
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    objects = UtilisateurManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        nom = self.get_full_name().strip()
        return nom if nom else self.email

    def get_type_utilisateur(self):
        """
        Retourne le type réel de l'utilisateur.
        """

        if Administrateur.objects.filter(pk=self.pk).exists():
            return "administrateur"

        if Agronome.objects.filter(pk=self.pk).exists():
            return "agronome"

        if Agriculteur.objects.filter(pk=self.pk).exists():
            return "agriculteur"

        return "utilisateur"


class Agriculteur(Utilisateur):

    class Meta:
        verbose_name = "Agriculteur"
        verbose_name_plural = "Agriculteurs"

    def consulter_predictions(self):
        """
        Retourne les prédictions de rendement
        associées à l'agriculteur.
        """
        pass

    def consulter_recommandations(self):
        """
        Retourne les recommandations
        destinées à l'agriculteur.
        """
        from services.recommandation_service import RecommendationService
        return RecommendationService.obtenir_recommandations_agriculteur(self)


class Agronome(Utilisateur):

    class Meta:
        verbose_name = "Agronome"
        verbose_name_plural = "Agronomes"

    def consulter_cultures(self):
        pass

    def consulter_observations(self):
        pass


class Administrateur(Utilisateur):

    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"

    def creer_utilisateur(self):
        pass

    def modifier_utilisateur(self):
        pass

    def supprimer_utilisateur(self):
        pass