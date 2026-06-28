"""Formulaire d'administration pour la gestion des utilisateurs.

Ce formulaire est utilisé par les vues d'administration pour créer et modifier
les comptes utilisateurs en ajoutant le type de profil et le mot de passe.
"""

from django import forms
from django.core.exceptions import ValidationError

from utilisateurs.models import Utilisateur


USER_TYPE_CHOICES = [
    ("utilisateur", "Utilisateur"),
    ("agriculteur", "Agriculteur"),
    ("agronome", "Agronome"),
    ("administrateur", "Administrateur"),
]


class UtilisateurForm(forms.ModelForm):
    """Formulaire de création et de modification d'un compte utilisateur."""

    type_utilisateur = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=False,
        label="Type d'utilisateur",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    mot_de_passe = forms.CharField(
        required=False,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Laissez vide pour conserver le mot de passe actuel.",
    )

    class Meta:
        model = Utilisateur
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
        ]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Adresse e-mail"}
            ),
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom d'utilisateur"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Prénom"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "email": "Adresse e-mail",
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "is_active": "Compte actif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["type_utilisateur"].initial = self.instance.get_type_utilisateur()
            self.fields["mot_de_passe"].required = False
        else:
            self.fields["type_utilisateur"].initial = "utilisateur"
            self.fields["mot_de_passe"].required = True

    def clean_email(self):
        """Valide l'unicité de l'adresse e-mail parmi les utilisateurs."""
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("L'adresse e-mail est obligatoire.")

        qs = Utilisateur.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Un utilisateur avec cette adresse e-mail existe déjà.")

        return email

    def clean_mot_de_passe(self):
        """Valide le mot de passe lors de la création d'un nouvel utilisateur."""
        mot_de_passe = self.cleaned_data.get("mot_de_passe")
        if not self.instance.pk and not mot_de_passe:
            raise ValidationError("Le mot de passe est obligatoire pour la création d'un utilisateur.")

        return mot_de_passe
