from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from utilisateurs.models import Agriculteur


class Culture(models.Model):
    """
    Représente une culture agricole associée à un agriculteur.
    """

    agriculteur = models.ForeignKey(
        Agriculteur,
        on_delete=models.CASCADE,
        related_name="cultures",
        verbose_name="Agriculteur",
    )

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la culture",
    )

    superficie = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Superficie (ha)",
    )

    localisation = models.CharField(
        max_length=255,
        verbose_name="Localisation",
    )

    date_semis = models.DateField(
        verbose_name="Date de semis",
        default=timezone.now,
    )

    statut = models.CharField(
        max_length=50,
        verbose_name="Statut",
        default="En cours",
    )

    class Meta:
        verbose_name = "Culture"
        verbose_name_plural = "Cultures"
        ordering = ["-date_semis"]
        indexes = [
            models.Index(fields=["nom"]),
            models.Index(fields=["date_semis"]),
            models.Index(fields=["localisation"]),
        ]
        unique_together = ("agriculteur", "nom")

    def __str__(self):
        return f"{self.nom} — {self.localisation}"

    def clean(self):
        if self.superficie <= 0:
            raise ValidationError({"superficie": "La superficie doit être supérieure à zéro."})

        if self.date_semis and self.date_semis > date.today():
            raise ValidationError(
                {"date_semis": "La date de semis ne peut pas être dans le futur."}
            )

    def age_en_jours(self):
        if not self.date_semis:
            return 0
        return (date.today() - self.date_semis).days

    def localisation_complete(self):
        return self.localisation.title()
