from django.contrib.auth.models import UserManager


class UtilisateurManager(UserManager):
    """
    Gestionnaire personnalisé des utilisateurs.

    Il centralise la création des différents types d'utilisateurs
    du système.
    """

    use_in_migrations = True