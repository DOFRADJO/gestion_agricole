from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from cultures.models import Culture


class Observation(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE, related_name="observations")
    description = models.TextField(blank=True, default="")
    date_observation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_observation"]

    def __str__(self):
        date_str = self.date_observation.date().isoformat() if self.date_observation else ""
        return f"{self.culture.nom} - {date_str}"

    def clean(self):
        if self.date_observation and self.date_observation > timezone.now():
            raise ValidationError("La date d'observation ne peut pas être dans le futur.")
