"""
Serializer for recipe API
"""
from rest_framework import serializers

from core.models import Recipe, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe"""
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'ingredients']
        read_only_fields = ['id']

    def _create_ingredients(self, ingredients: list, recipe: Recipe) -> None:
        """Handle the creation of ingredients"""
        for ingredient in ingredients:
            Ingredient.objects.create(
                **ingredient,
                recipe=recipe
            )

    def create(self, validated_data: dict) -> Recipe:
        """Create a recipe"""
        ingredients = validated_data.pop('ingredients', None)
        recipe = Recipe.objects.create(**validated_data)

        if ingredients:
            self._create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Update a recipe"""
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.all().delete()
            self._create_ingredients(ingredients, recipe=instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
