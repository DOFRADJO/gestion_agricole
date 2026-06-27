from django.contrib.auth import authenticate, login, logout
from services.utilisateur_service import UtilisateurService


class AuthenticationService:

    @staticmethod
    def authentifier(request, email, mot_de_passe):
        utilisateur = authenticate(
            request=request,
            username=email,
            password=mot_de_passe,
        )

        if utilisateur is not None and request is not None:
            login(request, utilisateur)

        return utilisateur

    @staticmethod
    def deconnecter(request):

        logout(request)

    @staticmethod
    def obtenir_dashboard(utilisateur):
        type_utilisateur = UtilisateurService.obtenir_type(utilisateur)

        correspondance = {
            "administrateur": "core:dashboard_admin",
            "agronome": "core:dashboard_agronome",
            "agriculteur": "core:dashboard_agriculteur",
        }

        return correspondance.get(type_utilisateur)