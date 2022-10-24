"""
Views for the recipe API
"""

from rest_framework import viewsets

from core.models import Recipe, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__startswith=name)
        return queryset.all().order_by('-name')


class IngredientViewSet(viewsets.GenericViewSet):
    """Manage ingredients in the database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        return self.queryset.all().order_by('-name')

    def perform_create(self, serializer):
        recipe = Recipe.objects.get(id=self.request.data['recipe'])
        serializer.save(recipe=recipe)
