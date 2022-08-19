from django.contrib import admin

from . import models

admin.site.register(models.Deck)
admin.site.register(models.Card)
admin.site.register(models.Test)
admin.site.register(models.Score)
admin.site.register(models.BoardDeck)
