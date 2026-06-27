from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ConnexionForm
from services.authentication_service import AuthenticationService


def connexion(request):
    """
    Affiche le formulaire de connexion.
    """

    if request.user.is_authenticated:

        destination = AuthenticationService.obtenir_dashboard(
            request.user
        )

        if destination:
            return redirect(destination)

        AuthenticationService.deconnecter(request)

        messages.error(
            request,
            "Votre compte ne possède aucun profil associé."
        )

        return redirect("authentication:connexion")

    formulaire = ConnexionForm()

    if request.method == "POST":

        formulaire = ConnexionForm(request.POST)

        if formulaire.is_valid():

            utilisateur = AuthenticationService.authentifier(
                request,
                formulaire.cleaned_data["email"],
                formulaire.cleaned_data["mot_de_passe"],
            )

            if utilisateur:

                destination = AuthenticationService.obtenir_dashboard(
                    utilisateur
                )

                if destination:
                    return redirect(destination)

                AuthenticationService.deconnecter(request)

                messages.error(
                    request,
                    "Votre compte ne possède aucun profil associé."
                )

                return redirect("authentication:connexion")

            messages.error(
                request,
                "Adresse e-mail ou mot de passe incorrect."
            )

    return render(
        request,
        "authentication/login.html",
        {
            "form": formulaire,
        },
    )


def deconnexion(request):
    """
    Déconnecte l'utilisateur.
    """

    AuthenticationService.deconnecter(request)

    return redirect("authentication:connexion")