from django.urls import reverse
from django.test import TestCase
from django.core.exceptions import PermissionDenied

from utilisateurs.models import Utilisateur
from services.utilisateur_service import UtilisateurService
from cultures.models import Culture
from observations.models import Observation
from predictions.models import Prediction
from services.prediction_service import PredictionService


class PredictionServiceTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="agri@example.com",
            username="agri",
            first_name="Alice",
            last_name="Dupont",
            password="password123",
        )
        self.agriculteur = UtilisateurService.creer_agriculteur(self.utilisateur)
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Blé",
            superficie=1.5,
            localisation="Champ central",
        )

    def test_generer_prediction_cree_une_prediction(self):
        prediction = PredictionService.generer_prediction(self.culture)

        self.assertEqual(Prediction.objects.count(), 1)
        self.assertEqual(prediction.culture, self.culture)
        self.assertGreaterEqual(prediction.rendementEstime, 0)
        self.assertGreaterEqual(prediction.niveauConfiance, 0)
        self.assertLessEqual(prediction.niveauConfiance, 1)

    def test_obtenir_prediction_genere_automatiquement_si_absente(self):
        prediction = PredictionService.obtenir_prediction(self.culture)
        self.assertIsNotNone(prediction)
        self.assertEqual(Prediction.objects.count(), 1)

    def test_recalculer_prediction_met_a_jour_la_prediction_du_jour(self):
        first_prediction = PredictionService.obtenir_prediction(self.culture)
        Observation.objects.create(culture=self.culture, description="Bon état")

        updated_prediction = PredictionService.recalculer_prediction(self.culture)

        self.assertEqual(Prediction.objects.count(), 1)
        self.assertGreaterEqual(updated_prediction.rendementEstime, first_prediction.rendementEstime)
        self.assertGreaterEqual(updated_prediction.niveauConfiance, first_prediction.niveauConfiance)

    def test_obtenir_predictions_agriculteur_restreint_aux_agriculteurs(self):
        predictions = PredictionService.obtenir_predictions_agriculteur(self.utilisateur)
        self.assertEqual(len(predictions), 1)

        agronome_user = Utilisateur.objects.create_user(
            email="agro@example.com",
            username="agro",
            first_name="Paul",
            last_name="Martin",
            password="password123",
        )
        UtilisateurService.creer_agronome(agronome_user)

        with self.assertRaises(PermissionDenied):
            PredictionService.obtenir_predictions_agriculteur(agronome_user)

    def test_historique_retourne_les_predictions_accessibles(self):
        PredictionService.obtenir_prediction(self.culture)
        historique = PredictionService.historique(self.utilisateur)
        self.assertEqual(historique.count(), 1)


class PredictionViewsTest(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="agri2@example.com",
            username="agri2",
            first_name="Claire",
            last_name="Bernard",
            password="password123",
        )
        self.agriculteur = UtilisateurService.creer_agriculteur(self.utilisateur)
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Tomates",
            superficie=0.8,
            localisation="Serre nord",
        )
        self.prediction = PredictionService.obtenir_prediction(self.culture)

    def test_liste_predictions_accessible_par_agriculteur(self):
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("predictions:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prédictions")

    def test_detail_prediction_accessible_par_agriculteur(self):
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("predictions:detail", args=[self.prediction.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rendement estimé")

    def test_historique_predictions_accessible_par_agriculteur(self):
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("predictions:historique"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historique des prédictions")

    def test_agriculteur_ne_peut_pas_voir_prediction_aliens(self):
        other_user = Utilisateur.objects.create_user(
            email="agri3@example.com",
            username="agri3",
            first_name="Louis",
            last_name="Petit",
            password="password123",
        )
        UtilisateurService.creer_agriculteur(other_user)
        other_culture = Culture.objects.create(
            agriculteur=other_user.agriculteur,
            nom="Pommes de terre",
            superficie=1.2,
            localisation="Nord",
        )
        other_prediction = PredictionService.obtenir_prediction(other_culture)

        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("predictions:detail", args=[other_prediction.pk]))
        self.assertEqual(response.status_code, 403)
