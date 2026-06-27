from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from cultures.forms import CultureForm
from cultures.models import Culture
from services.culture_service import CultureService
from services.utilisateur_service import UtilisateurService
from utilisateurs.models import Utilisateur


class CultureServiceTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="agri@test.com",
            username="agri",
            first_name="Jean",
            last_name="Dupont",
            password="password123",
        )
        self.agriculteur = UtilisateurService.creer_agriculteur(self.utilisateur)
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Tomates",
            superficie=1.5,
            date_plantation="2025-06-01",
            localisation="Champ central",
            description="Tomates bio",
        )

    def test_creer_culture_pour_agriculteur(self):
        formulaire = CultureForm(
            data={
                "nom": "Maïs",
                "superficie": 2.5,
                "date_plantation": "2025-08-01",
                "localisation": "Champ nord",
                "description": "Maïs de saison",
            },
            utilisateur=self.utilisateur,
        )
        self.assertTrue(formulaire.is_valid())
        culture = CultureService.creer_culture(self.utilisateur, formulaire)
        self.assertEqual(culture.agriculteur, self.agriculteur)
        self.assertEqual(culture.nom, "Maïs")

    def test_obtenir_cultures_filtre_recherche(self):
        resultat = CultureService.obtenir_cultures(
            self.utilisateur,
            {"q": "Tomates", "sort": "nom", "order": "asc"},
        )
        self.assertEqual(resultat["total"], 1)
        self.assertEqual(resultat["cultures"][0].nom, "Tomates")

    def test_modifier_culture(self):
        formulaire = CultureForm(
            data={
                "nom": "Tomates cerises",
                "superficie": 1.5,
                "date_plantation": "2025-06-01",
                "localisation": "Champ central",
                "description": "Tomates bio",
            },
            instance=self.culture,
            utilisateur=self.utilisateur,
        )
        self.assertTrue(formulaire.is_valid())
        culture_modifiee = CultureService.modifier_culture(
            self.utilisateur,
            self.culture,
            formulaire,
        )
        self.assertEqual(culture_modifiee.nom, "Tomates cerises")

    def test_supprimer_culture(self):
        CultureService.supprimer_culture(self.utilisateur, self.culture)
        self.assertFalse(Culture.objects.filter(pk=self.culture.pk).exists())

    def test_agronome_ne_peut_pas_modifier_une_culture_d_autrui(self):
        agronome_user = Utilisateur.objects.create_user(
            email="agro@test.com",
            username="agro",
            first_name="Claire",
            last_name="Martin",
            password="password123",
        )
        UtilisateurService.creer_agronome(agronome_user)
        formulaire = CultureForm(
            data={
                "nom": "Tomates rouges",
                "superficie": 1.5,
                "date_plantation": "2025-06-01",
                "localisation": "Champ central",
                "description": "Tomates bio",
            },
            instance=self.culture,
            utilisateur=agronome_user,
        )
        self.assertTrue(formulaire.is_valid())
        with self.assertRaises(PermissionDenied):
            CultureService.modifier_culture(agronome_user, self.culture, formulaire)


class CultureViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.utilisateur = Utilisateur.objects.create_user(
            email="agri@test.com",
            username="agri",
            first_name="Jean",
            last_name="Dupont",
            password="password123",
        )
        UtilisateurService.creer_agriculteur(self.utilisateur)
        self.client.login(email="agri@test.com", password="password123")

    def test_liste_cultures_accessible(self):
        response = self.client.get(reverse("cultures:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cultures/liste.html")

    def test_ajouter_culture_via_vue(self):
        response = self.client.post(
            reverse("cultures:ajouter"),
            {
                "nom": "Laitue",
                "superficie": 0.8,
                "date_plantation": "2025-09-01",
                "localisation": "Serre ouest",
                "description": "Laitues fraîches",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Culture.objects.filter(nom="Laitue").exists())

    def test_modifier_culture_via_vue(self):
        culture = Culture.objects.create(
            agriculteur=self.utilisateur.agriculteur,
            nom="Carottes",
            superficie=1.2,
            date_plantation="2025-07-01",
            localisation="Champ sud",
            description="Carottes locales",
        )
        response = self.client.post(
            reverse("cultures:modifier", args=[culture.pk]),
            {
                "nom": "Carottes bio",
                "superficie": 1.2,
                "date_plantation": "2025-07-01",
                "localisation": "Champ sud",
                "description": "Carottes locales",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        culture.refresh_from_db()
        self.assertEqual(culture.nom, "Carottes bio")

    def test_supprimer_culture_via_vue(self):
        culture = Culture.objects.create(
            agriculteur=self.utilisateur.agriculteur,
            nom="Courgette",
            superficie=0.9,
            date_plantation="2025-07-15",
            localisation="Serre est",
            description="Courgettes d'été",
        )
        response = self.client.post(
            reverse("cultures:supprimer", args=[culture.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Culture.objects.filter(pk=culture.pk).exists())
