"""
Views for the recipe API
"""

from rest_framework import viewsets

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all().order_by('-id')
