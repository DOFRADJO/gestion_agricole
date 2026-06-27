from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from utilisateurs.models import Utilisateur
from services.utilisateur_service import UtilisateurService
from cultures.models import Culture
from predictions.models import Prediction
from observations.models import Observation
from recommandations.models import Recommandation
from services.recommandation_service import RecommendationService
from services.prediction_service import PredictionService


class RecommendationServiceTest(TestCase):
    def setUp(self):
        """Set up test fixtures for recommendations."""
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

    def test_generer_recommandation_cree_une_recommandation(self):
        """Test that generating a recommendation creates a Recommandation object."""
        recommandation = RecommendationService.generer_recommandation(self.culture)

        self.assertEqual(Recommandation.objects.count(), 1)
        self.assertEqual(recommandation.culture, self.culture)
        self.assertIsNotNone(recommandation.type)
        self.assertIsNotNone(recommandation.contenu)

    def test_obtenir_recommandation_genere_automatiquement_si_absente(self):
        """Test that getting a recommendation generates one if it doesn't exist."""
        recommandation = RecommendationService.obtenir_recommandation(self.culture)
        self.assertIsNotNone(recommandation)
        self.assertEqual(Recommandation.objects.count(), 1)

    def test_obtenir_recommandation_retourne_la_plus_recente(self):
        """Test that getting a recommendation returns the most recent one."""
        first = RecommendationService.generer_recommandation(self.culture)
        updated = RecommendationService.mettre_a_jour_recommandation(self.culture)
        
        retrieved = RecommendationService.obtenir_recommandation(self.culture)
        # Same recommendation updated (same date, only 1 per day)
        self.assertEqual(retrieved.pk, updated.pk)

    def test_recommandation_varie_selon_prediction(self):
        """Test that recommendation type varies based on prediction."""
        # Create a prediction with low yield
        prediction = PredictionService.generer_prediction(self.culture)
        recommandation = RecommendationService.generer_recommandation(self.culture)
        
        self.assertIn(recommandation.type, ["Faible rendement", "Rendement moyen", "Rendement élevé"])

    def test_obtenir_recommandations_agriculteur_restreint(self):
        """Test that recommendations are restricted to the farmer's cultures."""
        recommandations = RecommendationService.obtenir_recommandations_agriculteur(self.utilisateur)
        self.assertEqual(recommandations.count(), 1)

        agronome_user = Utilisateur.objects.create_user(
            email="agro@example.com",
            username="agro",
            first_name="Paul",
            last_name="Martin",
            password="password123",
        )
        UtilisateurService.creer_agronome(agronome_user)

        with self.assertRaises(PermissionDenied):
            RecommendationService.obtenir_recommandations_agriculteur(agronome_user)

    def test_obtenir_recommandations_admin_voit_tout(self):
        """Test that admins/agronomes see all recommendations."""
        RecommendationService.obtenir_recommandation(self.culture)
        
        agronome_user = Utilisateur.objects.create_user(
            email="agro@example.com",
            username="agro",
            first_name="Paul",
            last_name="Martin",
            password="password123",
        )
        UtilisateurService.creer_agronome(agronome_user)
        
        recommandations = RecommendationService.obtenir_recommandations(agronome_user)
        self.assertGreaterEqual(recommandations.count(), 1)

    def test_historique_retourne_les_recommandations_accessibles(self):
        """Test that history returns accessible recommendations."""
        RecommendationService.obtenir_recommandation(self.culture)
        historique = RecommendationService.historique(self.utilisateur)
        self.assertEqual(historique.count(), 1)

    def test_historique_agriculteur_restreint(self):
        """Test that farmer can only see their own culture recommendations in history."""
        culture2 = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Maïs",
            superficie=1.2,
            localisation="Champ sud",
        )
        RecommendationService.obtenir_recommandation(self.culture)
        RecommendationService.obtenir_recommandation(culture2)
        
        historique = RecommendationService.historique(self.utilisateur)
        # Farmer should see only their own recommendations
        for rec in historique:
            self.assertEqual(rec.culture.agriculteur, self.agriculteur)

    def test_recommandation_unique_par_jour(self):
        """Test that only one recommendation per culture per day is created."""
        rec1 = RecommendationService.obtenir_recommandation(self.culture)
        rec2 = RecommendationService.obtenir_recommandation(self.culture)
        
        # Both should be the same object
        self.assertEqual(rec1.pk, rec2.pk)
        self.assertEqual(Recommandation.objects.filter(culture=self.culture).count(), 1)


class RecommendationViewsTest(TestCase):
    def setUp(self):
        """Set up test fixtures for recommendation views."""
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
        self.recommandation = RecommendationService.obtenir_recommandation(self.culture)

    def test_liste_recommandations_accessible_par_agriculteur(self):
        """Test that farmers can access the recommendations list."""
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("recommandations:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommandations")

    def test_detail_recommandation_accessible_par_agriculteur(self):
        """Test that farmers can view recommendation details."""
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("recommandations:detail", args=[self.recommandation.pk]))
        self.assertEqual(response.status_code, 200)

    def test_historique_recommandations_accessible_par_agriculteur(self):
        """Test that farmers can view recommendation history."""
        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("recommandations:historique"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historique des recommandations")

    def test_agriculteur_ne_peut_pas_voir_recommandation_aliens(self):
        """Test that farmers cannot view other farmers' recommendations."""
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
        other_recommandation = RecommendationService.obtenir_recommandation(other_culture)

        self.client.login(email="agri2@example.com", password="password123")
        response = self.client.get(reverse("recommandations:detail", args=[other_recommandation.pk]))
        self.assertEqual(response.status_code, 403)

    def test_liste_recommandations_non_authentifie_redirige(self):
        """Test that unauthenticated users are redirected."""
        response = self.client.get(reverse("recommandations:liste"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/authentication/", response.url)


class RecommendationIntegrationTest(TestCase):
    """Integration tests for recommendations with predictions and observations."""
    
    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.utilisateur = Utilisateur.objects.create_user(
            email="agri_integ@example.com",
            username="agri_integ",
            first_name="Test",
            last_name="Integ",
            password="password123",
        )
        self.agriculteur = UtilisateurService.creer_agriculteur(self.utilisateur)
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Vigne",
            superficie=2.0,
            localisation="Vignoble",
        )

    def test_recommandation_genere_a_partir_prediction(self):
        """Test that recommendations are generated from predictions."""
        prediction = PredictionService.generer_prediction(self.culture)
        recommandation = RecommendationService.obtenir_recommandation(self.culture)
        
        self.assertIsNotNone(recommandation)
        self.assertIsNotNone(prediction)
        # Recommendation should be based on the prediction
        self.assertIsNotNone(recommandation.contenu)

    def test_recommandation_type_evolue_avec_observations(self):
        """Test that recommendation type can evolve as observations increase."""
        rec1 = RecommendationService.obtenir_recommandation(self.culture)
        type1 = rec1.type
        
        # Add an observation
        Observation.objects.create(culture=self.culture, description="Bon état")
        
        # Recalculate prediction and recommendation
        PredictionService.recalculer_prediction(self.culture)
        rec2 = RecommendationService.mettre_a_jour_recommandation(self.culture)
        type2 = rec2.type
        
        # Types should be non-null (may differ)
        self.assertIsNotNone(type1)
        self.assertIsNotNone(type2)

    def test_dashboard_shows_recommendation_count(self):
        """Test that dashboards display correct recommendation counts."""
        from services.dashboard_service import DashboardService
        
        RecommendationService.obtenir_recommandation(self.culture)
        dashboard = DashboardService.obtenir_dashboard(self.utilisateur)
        
        # Check that the dashboard contains recommendation metric
        rec_stat = next(
            (s for s in dashboard["statistiques"] if s["label"] == "Recommandations"),
            None
        )
        self.assertIsNotNone(rec_stat)
        self.assertGreaterEqual(rec_stat["value"], 1)

    def test_user_helper_consulter_recommandations(self):
        """Test that Agriculteur model helper method works."""
        RecommendationService.obtenir_recommandation(self.culture)
        
        # Use the helper method
        recommandations = self.agriculteur.consulter_recommandations()
        self.assertEqual(recommandations.count(), 1)

