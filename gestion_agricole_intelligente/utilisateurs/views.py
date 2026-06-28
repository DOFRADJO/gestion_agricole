"""Vues d'administration pour la gestion des comptes utilisateurs.

Ces vues sont réservées aux administrateurs et permettent de lister,
créer, modifier et supprimer des comptes depuis l'interface.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render

from services.utilisateur_service import UtilisateurService
from utilisateurs.forms import UtilisateurForm
from utilisateurs.models import Utilisateur


def _verifier_administrateur(request):
    """Vérifie que l'utilisateur connecté est un administrateur."""
    if request.user.get_type_utilisateur() != "administrateur":
        raise PermissionDenied("Seul l'administrateur peut accéder à cette page.")


@login_required
def liste_utilisateurs(request):
    """Affiche la liste des utilisateurs avec les filtres de recherche."""
    _verifier_administrateur(request)
    resultat = UtilisateurService.obtenir_utilisateurs(request.GET)

    return render(
        request,
        "utilisateurs/liste.html",
        {
            "utilisateurs": resultat["utilisateurs"],
            "recherche": resultat["recherche"],
            "type_utilisateur": resultat["type_utilisateur"],
            "actif": resultat["actif"],
        },
    )


@login_required
def creer_utilisateur(request):
    """Affiche et traite le formulaire de création d'un nouvel utilisateur."""
    _verifier_administrateur(request)

    formulaire = UtilisateurForm(request.POST or None)

    if request.method == "POST" and formulaire.is_valid():
        UtilisateurService.creer_utilisateur(formulaire)
        messages.success(request, "L'utilisateur a été créé avec succès.")
        return redirect("utilisateurs:liste")

    return render(
        request,
        "utilisateurs/form.html",
        {
            "form": formulaire,
            "titre": "Créer un utilisateur",
            "action_label": "Créer",
        },
    )


@login_required
def modifier_utilisateur(request, pk):
    _verifier_administrateur(request)

    try:
        utilisateur = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        raise Http404("Utilisateur non trouvé.")

    formulaire = UtilisateurForm(request.POST or None, instance=utilisateur)

    if request.method == "POST" and formulaire.is_valid():
        if utilisateur.pk == request.user.pk and formulaire.cleaned_data["type_utilisateur"] != "administrateur":
            formulaire.add_error(
                "type_utilisateur",
                "Vous ne pouvez pas retirer vous-même le rôle administrateur.",
            )

        if utilisateur.pk == request.user.pk and not formulaire.cleaned_data["is_active"]:
            formulaire.add_error(
                "is_active",
                "Vous ne pouvez pas désactiver votre propre compte.",
            )

        if formulaire.is_valid():
            UtilisateurService.modifier_utilisateur(formulaire, utilisateur)
            messages.success(request, "L'utilisateur a été modifié avec succès.")
            return redirect("utilisateurs:liste")

    return render(
        request,
        "utilisateurs/form.html",
        {
            "form": formulaire,
            "titre": "Modifier un utilisateur",
            "action_label": "Enregistrer",
            "utilisateur": utilisateur,
        },
    )


@login_required
def supprimer_utilisateur(request, pk):
    _verifier_administrateur(request)

    try:
        utilisateur = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        raise Http404("Utilisateur non trouvé.")

    if utilisateur.pk == request.user.pk:
        raise PermissionDenied("Vous ne pouvez pas supprimer votre propre compte.")

    if request.method == "POST":
        UtilisateurService.supprimer_utilisateur(utilisateur)
        messages.success(request, "L'utilisateur a été supprimé avec succès.")
        return redirect("utilisateurs:liste")

    return render(
        request,
        "utilisateurs/supprimer.html",
        {
            "utilisateur": utilisateur,
        },
    )
