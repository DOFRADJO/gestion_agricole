from django import forms

from .models import Culture


class CultureForm(forms.ModelForm):

    class Meta:

        model = Culture

        fields = [

            "nom",

            "superficie",

            "date_plantation",

            "localisation",

            "description",

        ]

        widgets = {

            "nom": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "superficie": forms.NumberInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "date_plantation": forms.DateInput(

                attrs={

                    "class": "form-control",

                    "type": "date",

                }

            ),

            "localisation": forms.TextInput(

                attrs={

                    "class": "form-control",

                }

            ),

            "description": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 4,

                }

            ),

        }