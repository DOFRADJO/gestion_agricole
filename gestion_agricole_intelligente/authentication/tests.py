from django.test import TestCase, Client
from django.urls import reverse
from utilisateurs.models import Utilisateur, Administrateur, Agronome, Agriculteur
from services.utilisateur_service import UtilisateurService
from services.authentication_service import AuthenticationService


class AuthenticationViewsTest(TestCase):
    """Tests du formulaire et de la vue de connexion."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("authentication:connexion")

        self.utilisateur_admin = Utilisateur.objects.create_user(
            email="admin@test.com",
            username="admin",
            first_name="Admin",
            last_name="Test",
            password="password123",
        )
        UtilisateurService.creer_administrateur(self.utilisateur_admin)

        self.utilisateur_agronome = Utilisateur.objects.create_user(
            email="agronome@test.com",
            username="agronome",
            first_name="Agronome",
            last_name="Test",
            password="password123",
        )
        UtilisateurService.creer_agronome(self.utilisateur_agronome)

        self.utilisateur_agriculteur = Utilisateur.objects.create_user(
            email="agriculteur@test.com",
            username="agriculteur",
            first_name="Agriculteur",
            last_name="Test",
            password="password123",
        )
        UtilisateurService.creer_agriculteur(self.utilisateur_agriculteur)

    def test_login_page_accessible(self):
        """Le formulaire de connexion est accessible."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authentication/login.html")

    def test_valid_admin_login_redirects_to_admin_dashboard(self):
        """Un administrateur valide est redirigé vers le dashboard admin."""
        response = self.client.post(
            self.login_url,
            {"email": "admin@test.com", "mot_de_passe": "password123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard/administrateur", response.request["PATH_INFO"])

    def test_valid_agronome_login_redirects_to_agronome_dashboard(self):
        """Un agronome valide est redirigé vers le dashboard agronome."""
        response = self.client.post(
            self.login_url,
            {"email": "agronome@test.com", "mot_de_passe": "password123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard/agronome", response.request["PATH_INFO"])

    def test_valid_agriculteur_login_redirects_to_agriculteur_dashboard(self):
        """Un agriculteur valide est redirigé vers le dashboard agriculteur."""
        response = self.client.post(
            self.login_url,
            {"email": "agriculteur@test.com", "mot_de_passe": "password123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dashboard/agriculteur", response.request["PATH_INFO"])

    def test_invalid_email_login_fails(self):
        """Une adresse email invalide échoue la connexion."""
        response = self.client.post(
            self.login_url,
            {"email": "nonexistent@test.com", "mot_de_passe": "password123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", None, None)

    def test_invalid_password_login_fails(self):
        """Un mot de passe invalide échoue la connexion."""
        response = self.client.post(
            self.login_url,
            {"email": "admin@test.com", "mot_de_passe": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", None, None)

    def test_logout_clears_session(self):
        """La déconnexion efface la session."""
        self.client.login(email="admin@test.com", password="password123")
        response = self.client.get(reverse("authentication:deconnexion"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


class AuthenticationServiceTest(TestCase):
    """Tests du service d'authentification."""

    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="test@test.com",
            username="test",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        UtilisateurService.creer_administrateur(self.utilisateur)

    def test_authentifier_returns_user_on_success(self):
        """Le service d'authentification retourne l'utilisateur si le login est correct."""
        user = AuthenticationService.authentifier(
            None,
            "test@test.com",
            "password123",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@test.com")

    def test_authentifier_returns_none_on_failure(self):
        """Le service d'authentification retourne None si le login est incorrect."""
        user = AuthenticationService.authentifier(
            None,
            "test@test.com",
            "wrongpassword",
        )
        self.assertIsNone(user)

    def test_obtenir_dashboard_admin(self):
        """Le service retourne le bon dashboard pour un administrateur."""
        dashboard = AuthenticationService.obtenir_dashboard(self.utilisateur)
        self.assertEqual(dashboard, "core:dashboard_admin")

    def test_obtenir_dashboard_agronome(self):
        """Le service retourne le bon dashboard pour un agronome."""
        agronome = Utilisateur.objects.create_user(
            email="agronome@test.com",
            username="agronome",
            first_name="Agronome",
            last_name="User",
            password="password123",
        )
        UtilisateurService.creer_agronome(agronome)

        dashboard = AuthenticationService.obtenir_dashboard(agronome)
        self.assertEqual(dashboard, "core:dashboard_agronome")

    def test_obtenir_dashboard_agriculteur(self):
        """Le service retourne le bon dashboard pour un agriculteur."""
        agriculteur = Utilisateur.objects.create_user(
            email="agriculteur@test.com",
            username="agriculteur",
            first_name="Agriculteur",
            last_name="User",
            password="password123",
        )
        UtilisateurService.creer_agriculteur(agriculteur)

        dashboard = AuthenticationService.obtenir_dashboard(agriculteur)
        self.assertEqual(dashboard, "core:dashboard_agriculteur")

    def test_obtenir_dashboard_no_profile_returns_none(self):
        """Le service retourne None si l'utilisateur n'a pas de profil."""
        utilisateur_sans_profil = Utilisateur.objects.create_user(
            email="noprofile@test.com",
            username="noprofile",
            first_name="No",
            last_name="Profile",
            password="password123",
        )

        dashboard = AuthenticationService.obtenir_dashboard(utilisateur_sans_profil)
        self.assertIsNone(dashboard)
