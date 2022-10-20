"""
Test for models
"""
from django.test import TestCase

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        recipe = models.Recipe.objects.create(
            name='Bacon Butty',
            description='A perfect meal for a lazy sunday',
        )

        self.assertEqual(str(recipe), recipe.name)

    def test_create_ingredient(self):
        """Test creating a recipe is successful"""
        recipe = models.Recipe.objects.create(
            name='Bacon Butty',
            description='A perfect meal for a lazy sunday',
        )
        ingredient = models.Ingredient.objects.create(
            name='Bacon',
            recipe=recipe
        )
        self.assertEqual(str(ingredient), ingredient.name)
