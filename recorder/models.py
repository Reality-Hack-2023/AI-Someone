from django import forms
from django.db import models


# Create your models here.
class Scene(models.Model):
    name = models.CharField(max_length=100)
    speech = models.TextField(max_length=10000, null=True, blank=True)
    background = models.FileField(upload_to='static/images')
    scene_prompts = models.TextField(max_length=10000)
