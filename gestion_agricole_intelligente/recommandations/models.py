from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cultures.models import Culture


class Recommandation(models.Model):
    culture = models.ForeignKey(
        Culture,
        on_delete=models.CASCADE,
        related_name="recommandations",
        verbose_name="Culture",
    )
    dateRecommandation = models.DateField(
        verbose_name="Date de recommandation",
        default=timezone.localdate,
    )
    type = models.CharField(
        max_length=100,
        verbose_name="Type de recommandation",
    )
    contenu = models.TextField(
        verbose_name="Contenu de la recommandation",
    )

    class Meta:
        verbose_name = "Recommandation"
        verbose_name_plural = "Recommandations"
        ordering = ["-dateRecommandation", "-id"]
        indexes = [
            models.Index(fields=["dateRecommandation"]),
            models.Index(fields=["culture"]),
        ]
        unique_together = ("culture", "dateRecommandation")

    def __str__(self):
        return f"Recommandation {self.culture.nom} ({self.dateRecommandation})"

    def clean(self):
        if self.dateRecommandation and self.dateRecommandation > timezone.localdate():
            raise ValidationError(
                {"dateRecommandation": "La date de recommandation ne peut pas être dans le futur."}
            )

        if not self.type:
            raise ValidationError({"type": "Le type de recommandation est requis."})

        if not self.contenu:
            raise ValidationError({"contenu": "Le contenu de la recommandation est requis."})
