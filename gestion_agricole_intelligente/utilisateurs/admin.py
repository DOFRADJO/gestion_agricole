from django.contrib import admin

from .models import (
    Utilisateur,
    Agriculteur,
    Agronome,
    Administrateur,
)

admin.site.register(Utilisateur)
admin.site.register(Agriculteur)
admin.site.register(Agronome)
admin.site.register(Administrateur)