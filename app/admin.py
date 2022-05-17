from django.contrib import admin

# Register your models here.
from app import models

admin.site.register(models.Log)
admin.site.register(models.Live)
admin.site.register(models.Label)
admin.site.register(models.Push)

