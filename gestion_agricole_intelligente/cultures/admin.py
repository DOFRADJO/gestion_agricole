from django.contrib import admin

from .models import Culture


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):

    list_display = (

        "nom",

        "agriculteur",

        "superficie",

        "date_plantation",

    )

    search_fields = (

        "nom",

        "localisation",

    )

    list_filter = (

        "date_plantation",

    )