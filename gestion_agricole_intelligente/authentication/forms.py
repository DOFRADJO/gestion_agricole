from django import forms


class ConnexionForm(forms.Form):

    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Adresse e-mail",
                "autocomplete": "email",
            }
        ),
    )

    mot_de_passe = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mot de passe",
                "autocomplete": "current-password",
            }
        ),
    )