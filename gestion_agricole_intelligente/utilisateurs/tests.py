from django.test import TestCase
from django.contrib.auth.models import Group

from services.utilisateur_service import UtilisateurService
from utilisateurs.models import Administrateur, Utilisateur, Agronome, Agriculteur


class UtilisateurManagerTest(TestCase):
    """Tests du gestionnaire personnalisé d'utilisateurs."""

    def test_create_user_with_email(self):
        """Un utilisateur peut être créé avec un email."""
        utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            username="test",
            first_name="Test",
            last_name="User",
            password="password123",
        )

        self.assertEqual(utilisateur.email, "test@example.com")
        self.assertTrue(utilisateur.check_password("password123"))

    def test_create_user_sets_default_username_from_email(self):
        """Si username n'est pas spécifié, il est défini à partir de l'email."""
        utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )

        self.assertIsNotNone(utilisateur.username)

    def test_create_superuser(self):
        """Un superutilisateur peut être créé."""
        utilisateur = Utilisateur.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            password="adminpass",
        )

        self.assertTrue(utilisateur.is_superuser)
        self.assertTrue(utilisateur.is_staff)
        self.assertTrue(utilisateur.is_active)

    def test_create_superuser_requires_email(self):
        """Un superutilisateur ne peut pas être créé sans email."""
        with self.assertRaises(ValueError):
            Utilisateur.objects.create_superuser(
                email="",
                username="admin",
                first_name="Admin",
                last_name="User",
                password="adminpass",
            )


class UtilisateurServiceTest(TestCase):
    """Tests du service de gestion des utilisateurs."""

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            username="test",
            first_name="Test",
            last_name="User",
            password="password123",
        )

    def test_creer_administrateur_creates_subclass(self):
        """La création d'un administrateur crée bien la ligne de sous-classe."""
        admin = UtilisateurService.creer_administrateur(self.utilisateur)

        self.assertEqual(admin.pk, self.utilisateur.pk)
        self.assertTrue(Administrateur.objects.filter(pk=self.utilisateur.pk).exists())

    def test_creer_administrateur_adds_to_group(self):
        """La création d'un administrateur l'ajoute au groupe Administrateurs."""
        UtilisateurService.creer_administrateur(self.utilisateur)

        groupe = Group.objects.get(name="Administrateurs")
        self.assertTrue(self.utilisateur.groups.filter(pk=groupe.pk).exists())

    def test_creer_agronome_creates_subclass(self):
        """La création d'un agronome crée bien la ligne de sous-classe."""
        agronome = UtilisateurService.creer_agronome(self.utilisateur)

        self.assertEqual(agronome.pk, self.utilisateur.pk)
        self.assertTrue(Agronome.objects.filter(pk=self.utilisateur.pk).exists())

    def test_creer_agronome_adds_to_group(self):
        """La création d'un agronome l'ajoute au groupe Agronomes."""
        UtilisateurService.creer_agronome(self.utilisateur)

        groupe = Group.objects.get(name="Agronomes")
        self.assertTrue(self.utilisateur.groups.filter(pk=groupe.pk).exists())

    def test_creer_agriculteur_creates_subclass(self):
        """La création d'un agriculteur crée bien la ligne de sous-classe."""
        agriculteur = UtilisateurService.creer_agriculteur(self.utilisateur)

        self.assertEqual(agriculteur.pk, self.utilisateur.pk)
        self.assertTrue(Agriculteur.objects.filter(pk=self.utilisateur.pk).exists())

    def test_creer_agriculteur_adds_to_group(self):
        """La création d'un agriculteur l'ajoute au groupe Agriculteurs."""
        UtilisateurService.creer_agriculteur(self.utilisateur)

        groupe = Group.objects.get(name="Agriculteurs")
        self.assertTrue(self.utilisateur.groups.filter(pk=groupe.pk).exists())

    def test_obtenir_type_administrateur(self):
        """Le service détecte correctement un administrateur."""
        UtilisateurService.creer_administrateur(self.utilisateur)

        type_utilisateur = UtilisateurService.obtenir_type(self.utilisateur)
        self.assertEqual(type_utilisateur, "administrateur")

    def test_obtenir_type_agronome(self):
        """Le service détecte correctement un agronome."""
        UtilisateurService.creer_agronome(self.utilisateur)

        type_utilisateur = UtilisateurService.obtenir_type(self.utilisateur)
        self.assertEqual(type_utilisateur, "agronome")

    def test_obtenir_type_agriculteur(self):
        """Le service détecte correctement un agriculteur."""
        UtilisateurService.creer_agriculteur(self.utilisateur)

        type_utilisateur = UtilisateurService.obtenir_type(self.utilisateur)
        self.assertEqual(type_utilisateur, "agriculteur")

    def test_obtenir_type_no_profile_returns_utilisateur(self):
        """Le service retourne 'utilisateur' si aucun profil n'existe."""
        type_utilisateur = UtilisateurService.obtenir_type(self.utilisateur)
        self.assertEqual(type_utilisateur, "utilisateur")

    def test_creer_sous_classe_idempotent(self):
        """Créer un profil deux fois n'en crée qu'un."""
        UtilisateurService.creer_administrateur(self.utilisateur)
        count1 = Administrateur.objects.filter(pk=self.utilisateur.pk).count()

        UtilisateurService.creer_administrateur(self.utilisateur)
        count2 = Administrateur.objects.filter(pk=self.utilisateur.pk).count()

        self.assertEqual(count1, 1)
        self.assertEqual(count2, 1)


class UtilisateurModelTest(TestCase):
    """Tests du modèle Utilisateur."""

    def test_utilisateur_str_returns_full_name(self):
        """L'affichage de l'utilisateur montre son nom complet."""
        utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            username="test",
            first_name="John",
            last_name="Doe",
            password="password123",
        )

        self.assertEqual(str(utilisateur), "John Doe")

    def test_utilisateur_str_returns_email_if_no_name(self):
        """L'affichage de l'utilisateur montre l'email s'il n'a pas de nom."""
        utilisateur = Utilisateur.objects.create_user(
            email="test@example.com",
            username="test",
            password="password123",
        )

        self.assertEqual(str(utilisateur), "test@example.com")

    def test_get_type_utilisateur_administrateur(self):
        """La détection du type retourne 'administrateur'."""
        utilisateur = Utilisateur.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="password123",
        )
        Administrateur.objects.create(
            pk=utilisateur.pk,
            email=utilisateur.email,
            username=utilisateur.username,
            password=utilisateur.password,
        )

        self.assertEqual(utilisateur.get_type_utilisateur(), "administrateur")

    def test_get_type_utilisateur_no_profile(self):
        """La détection du type retourne 'utilisateur' si aucun profil."""
        utilisateur = Utilisateur.objects.create_user(
            email="noProfile@example.com",
            username="noprofile",
            password="password123",
        )

        self.assertEqual(utilisateur.get_type_utilisateur(), "utilisateur")
