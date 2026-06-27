from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from utilisateurs.models import Utilisateur, Administrateur
from services.utilisateur_service import UtilisateurService

GROUPES = (
    "Administrateurs",
    "Agronomes",
    "Agriculteurs",
)


class Command(BaseCommand):
    help = "Initialise les données de base de l'application."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="admin@gestion-agricole.local",
            help="Email du premier administrateur"
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Mot de passe du premier administrateur"
        )

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("🚀 Initialisation de l'application"))
        self.stdout.write("")

        self.create_groups()
        self.create_first_admin(
            email=options["email"],
            password=options["password"]
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("✅ Initialisation terminée avec succès!")
        )
        self.stdout.write("")

    def create_groups(self):
        """Crée les trois groupes de l'application."""
        self.stdout.write(self.style.SUCCESS("📋 Création des groupes..."))

        for groupe in GROUPES:
            obj, created = Group.objects.get_or_create(name=groupe)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Groupe '{groupe}' créé")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⓘ Groupe '{groupe}' existe déjà")
                )

    def create_first_admin(self, email, password):
        """Crée le premier administrateur si aucun n'existe."""
        self.stdout.write(self.style.SUCCESS("👤 Création du premier administrateur..."))

        if Administrateur.objects.exists():
            self.stdout.write(
                self.style.WARNING("  ⓘ Un administrateur existe déjà")
            )
            return

        utilisateur = Utilisateur.objects.create_superuser(
            email=email,
            username=email,
            first_name="Admin",
            last_name="Système",
            password=password,
        )

        UtilisateurService.creer_administrateur(utilisateur)

        self.stdout.write(
            self.style.SUCCESS(f"  ✓ Administrateur créé: {email}")
        )
