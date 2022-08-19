from django import forms
from django.forms import ModelForm

from .models import Card, Deck


####---- Deck ------------------------------
class DeckModelForm(ModelForm):
    class Meta:
        model = Deck
        fields = [
            "deck_name",
            "description",
        ]
        labels = {
            "deck_name": "Name",
            "description": "Description",
        }
        widgets = {
            "deck_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Deck name...",
                    "required": True,
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Deck description...",
                }
            ),
        }


####---- Card ------------------------------
class CardModelForm(ModelForm):
    class Meta:
        model = Card
        fields = {
            "front",
            "back",
            "extra_info",
        }
        labels = {
            "front": "Question",
            "back": "Answer",
            "extra_info": "Extra information",
        }
