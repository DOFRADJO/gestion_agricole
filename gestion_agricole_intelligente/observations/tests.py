from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from utilisateurs.models import Agriculteur, Agronome
from cultures.models import Culture
from observations.models import Observation


class ObservationModelTest(TestCase):
    def setUp(self):
        self.agriculteur = Agriculteur.objects.create_user(
            email="agri@example.com",
            password="pass",
            first_name="Agri",
            last_name="One",
        )
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Test",
            superficie=1.5,
            date_semis=timezone.now().date(),
            localisation="Ferme X",
            statut="En cours",
        )

    def test_create_observation(self):
        obs = Observation.objects.create(
            culture=self.culture,
            description="Début de croissance observé",
        )
        self.assertTrue(str(obs).startswith(self.culture.nom))
        self.assertEqual(Observation.objects.count(), 1)


class ObservationViewsTest(TestCase):
    def setUp(self):
        self.agriculteur = Agriculteur.objects.create_user(
            email="agri2@example.com",
            password="pass",
            first_name="Agri2",
            last_name="Two",
        )
        self.agronome = Agronome.objects.create_user(
            email="agro@example.com",
            password="pass",
            first_name="Agro",
            last_name="One",
        )
        self.culture = Culture.objects.create(
            agriculteur=self.agriculteur,
            nom="Test2",
            superficie=2.0,
            date_semis=timezone.now().date(),
            localisation="Ferme Y",
            statut="En cours",
        )

    def test_list_requires_login(self):
        url = reverse("observations:liste")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_agriculteur_can_add_observation(self):
        self.client.login(email="agri2@example.com", password="pass")
        response = self.client.post(
            reverse("observations:ajouter"),
            {
                "culture": self.culture.pk,
                "description": "Nouvelle observation",
                "date_observation": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Observation.objects.count(), 1)

    def test_agronome_cannot_add_observation(self):
        self.client.login(email="agro@example.com", password="pass")
        response = self.client.post(
            reverse("observations:ajouter"),
            {
                "culture": self.culture.pk,
                "description": "Observation agronome",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Observation.objects.count(), 0)

    def test_agronome_can_view_observation_list(self):
        self.client.login(email="agro@example.com", password="pass")
        response = self.client.get(reverse("observations:liste"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "observations/liste.html")
