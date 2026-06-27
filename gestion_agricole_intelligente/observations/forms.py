from django import forms
from django.utils import timezone

from .models import Observation


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = ["culture", "description", "date_observation"]
        widgets = {
            "date_observation": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Description de l'observation",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        utilisateur = kwargs.pop("utilisateur", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.date_observation:
            dt = self.instance.date_observation
            self.initial["date_observation"] = dt.strftime("%Y-%m-%dT%H:%M")

        if utilisateur and utilisateur.get_type_utilisateur() == "agriculteur":
            self.fields["culture"].queryset = self.fields["culture"].queryset.filter(agriculteur=utilisateur.agriculteur)

        self.fields["date_observation"].required = False

    def clean_date_observation(self):
        dt = self.cleaned_data.get("date_observation")
        if dt and dt > timezone.now():
            raise forms.ValidationError("La date d'observation ne peut pas être dans le futur.")
        return dt

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("date_observation"):
            cleaned["date_observation"] = timezone.now()
        return cleaned
