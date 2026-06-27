from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cultures.models import Culture


class Prediction(models.Model):
    culture = models.ForeignKey(
        Culture,
        on_delete=models.CASCADE,
        related_name="predictions",
        verbose_name="Culture",
    )
    datePrediction = models.DateField(
        verbose_name="Date de prédiction",
        default=timezone.localdate,
    )
    rendementEstime = models.FloatField(
        verbose_name="Rendement estimé",
    )
    niveauConfiance = models.FloatField(
        verbose_name="Niveau de confiance",
    )
    commentaires = models.TextField(
        blank=True,
        default="",
        verbose_name="Commentaires",
    )

    class Meta:
        verbose_name = "Prédiction"
        verbose_name_plural = "Prédictions"
        ordering = ["-datePrediction", "-id"]
        indexes = [
            models.Index(fields=["datePrediction"]),
            models.Index(fields=["culture"]),
        ]

    def __str__(self):
        return f"Prédiction {self.culture.nom} ({self.datePrediction})"

    def clean(self):
        if self.datePrediction and self.datePrediction > timezone.localdate():
            raise ValidationError(
                {"datePrediction": "La date de prédiction ne peut pas être dans le futur."}
            )

        if self.rendementEstime < 0:
            raise ValidationError(
                {"rendementEstime": "Le rendement estimé doit être supérieur ou égal à zéro."}
            )

        if not (0.0 <= self.niveauConfiance <= 1.0):
            raise ValidationError(
                {
                    "niveauConfiance": (
                        "Le niveau de confiance doit être compris entre 0.0 et 1.0."
                    )
                }
            )
