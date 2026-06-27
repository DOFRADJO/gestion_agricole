from django.contrib.auth.base_user import BaseUserManager


class UtilisateurManager(BaseUserManager):
    """
    Gestionnaire personnalisé des utilisateurs.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)

        utilisateur = self.model(
            email=email,
            **extra_fields,
        )

        utilisateur.set_password(password)
        utilisateur.save(using=self._db)

        return utilisateur

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("username", email)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)