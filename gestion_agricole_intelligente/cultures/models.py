from django.db import models

from utilisateurs.models import Agriculteur


class Culture(models.Model):
    """
    Représente une culture agricole.
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

    date_plantation = models.DateField(
        verbose_name="Date de plantation",
    )

    localisation = models.CharField(
        max_length=255,
        verbose_name="Localisation",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
    )

    date_modification = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Culture"
        verbose_name_plural = "Cultures"
        ordering = ["-date_creation"]

    def __str__(self):
        return self.nom