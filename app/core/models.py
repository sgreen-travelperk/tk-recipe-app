"""
Database models
"""
from django.db import models


class Recipe(models.Model):
    """Recipe object"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
