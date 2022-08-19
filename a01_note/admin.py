from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Page)
admin.site.register(models.PropertyType)
admin.site.register(models.PageProperty)

admin.site.register(models.Access)

admin.site.register(models.Tag)
admin.site.register(models.WebmarkProperty)

admin.site.register(models.TextContent)
admin.site.register(models.ImageContent)
admin.site.register(models.FileContent)
admin.site.register(models.WebmarkContent)

admin.site.register(models.BlockIndex)
admin.site.register(models.BlockType)
