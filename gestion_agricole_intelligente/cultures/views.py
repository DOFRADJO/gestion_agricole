from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import CultureForm

from services.culture_service import CultureService


@login_required
def liste_cultures(request):

    cultures = CultureService.obtenir_cultures(

        request.user

    )

    return render(

        request,

        "cultures/liste.html",

        {

            "cultures": cultures,

        },

    )


@login_required
def ajouter_culture(request):

    formulaire = CultureForm()

    if request.method == "POST":

        formulaire = CultureForm(request.POST)

        if formulaire.is_valid():

            CultureService.creer_culture(

                request.user,

                formulaire,

            )

            return redirect(

                "cultures:liste"

            )

    return render(

        request,

        "cultures/ajouter.html",

        {

            "form": formulaire,

        },

    )