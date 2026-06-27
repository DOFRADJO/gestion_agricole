from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from utilisateurs.models import Agriculteur
from .models import Culture


class CultureForm(forms.ModelForm):
    class Meta:
        model = Culture
        fields = [
            "agriculteur",
            "nom",
            "superficie",
            "date_plantation",
            "localisation",
            "description",
        ]
        widgets = {
            "agriculteur": forms.Select(
                attrs={"class": "form-select"}
            ),
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de la culture",
                }
            ),
            "superficie": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Superficie en hectares",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "date_plantation": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
            ),
            "localisation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ville, région ou ferme",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Description de la culture",
                }
            ),
        }
        labels = {
            "agriculteur": "Agriculteur",
            "nom": "Nom de la culture",
            "superficie": "Superficie (ha)",
            "date_plantation": "Date de plantation",
            "localisation": "Localisation",
            "description": "Description",
        }

    def __init__(self, *args, utilisateur=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.utilisateur = utilisateur

        # Ensure date field initial value is formatted for HTML date inputs (YYYY-MM-DD)
        if self.instance and getattr(self.instance, 'date_plantation', None):
            try:
                self.initial.setdefault('date_plantation', self.instance.date_plantation.strftime('%Y-%m-%d'))
            except Exception:
                pass

        if utilisateur and utilisateur.get_type_utilisateur() == "agriculteur":
            self.fields.pop("agriculteur", None)
        else:
            self.fields["agriculteur"].queryset = Agriculteur.objects.order_by(
                "first_name", "last_name"
            )
            self.fields["agriculteur"].empty_label = "Sélectionner un agriculteur"
            if self.instance and self.instance.pk:
                self.fields["agriculteur"].required = False

    def clean_superficie(self):
        superficie = self.cleaned_data.get("superficie")
        if superficie is None or superficie <= 0:
            raise ValidationError("La superficie doit être supérieure à zéro.")
        return superficie

    def clean_agriculteur(self):
        agriculteur = self.cleaned_data.get("agriculteur")
        if self.instance and self.instance.pk and agriculteur is None:
            return self.instance.agriculteur
        return agriculteur

    def clean(self):
        super().clean()
        date_plantation = self.cleaned_data.get("date_plantation")
        if date_plantation and date_plantation > date.today():
            raise ValidationError(
                {
                    "date_plantation": "La date de plantation ne peut pas être dans le futur."
                }
            )
