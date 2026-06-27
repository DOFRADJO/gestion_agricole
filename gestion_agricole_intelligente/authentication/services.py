from django.contrib.auth import authenticate


class AuthenticationService:
    """
    Service responsable de l'authentification.
    """

    @staticmethod
    def authentifier(email, mot_de_passe):
        """
        Authentifie un utilisateur.
        """

        utilisateur = authenticate(
            username=email,
            password=mot_de_passe,
        )

        return utilisateur