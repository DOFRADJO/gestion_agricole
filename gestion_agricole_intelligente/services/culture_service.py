from cultures.models import Culture


class CultureService:

    """
    Gestion des cultures.
    """

    @staticmethod
    def creer_culture(utilisateur, formulaire):

        culture = formulaire.save(commit=False)

        culture.agriculteur = utilisateur.agriculteur

        culture.save()

        return culture

    @staticmethod
    def obtenir_cultures(utilisateur):

        return Culture.objects.filter(

            agriculteur=utilisateur.agriculteur

        )