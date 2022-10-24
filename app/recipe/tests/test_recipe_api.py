"""
Tests for recipe API
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id: int) -> str:
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(**params: dict) -> Recipe:
    """Create and return a sample recipe"""
    defaults = {
        'name': 'Sample recipe name',
        'description': 'Sample description',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(**defaults)
    return recipe


class RecipeAPITests(TestCase):
    """Tests for recipe API requests"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_recipe(self) -> None:
        """Test creating a recipe"""
        payload = {
            'name': 'Sample recipe Test',
            'description': 'Sample description Test',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_retrieve_recipe_list(self) -> None:
        """Test retrieving a list of recipes"""
        create_recipe(name='Sample recipe name 1')
        create_recipe(name='Sample recipe name 2')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-name')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self) -> None:
        """Test get recipe detail"""
        recipe = create_recipe()

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_full_update_of_recipe(self) -> None:
        """Test full update of recipe"""
        recipe = create_recipe()

        payload = {
            'name': 'New recipe name',
            'description': 'New recipe description'
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_partial_update_of_recipe(self) -> None:
        """Test partial update of a recipe"""
        original_name = 'Cake of the Day'
        original_desc = 'A fluffy and spongy cake'
        recipe = create_recipe(
            name=original_name,
            description=original_desc
        )

        payload = {'description': 'A dense and chocolatey cake'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, original_name)
        self.assertEqual(recipe.description, payload['description'])

    def test_delete_recipe(self) -> None:
        """Test deleting a recipe successful"""
        recipe = create_recipe()

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_ingredients(self) -> None:
        """Test creating a recipe with ingredients"""
        payload = {
            'name': 'Sample recipe with Ingredients',
            'description': 'Sample description Test',
            'ingredients': [
                {'name': 'ingredient 1'},
                {'name': 'ingredient 2'}
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self) -> None:
        """Test creating a recipe with existing ingredients"""
        ingredient_common = {'name': 'ingredient 2'}
        payload1 = {
            'name': 'Pancakes',
            'description': 'Sample description',
            'ingredients': [
                {'name': 'ingredient 1'},
                ingredient_common
            ]
        }

        payload2 = {
            'name': 'Eggs on toast',
            'description': 'Sample description',
            'ingredients': [
                {'name': 'ingredient 3'},
                ingredient_common
            ]
        }

        res1 = self.client.post(RECIPES_URL, payload1, format='json')
        res2 = self.client.post(RECIPES_URL, payload2, format='json')

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        recipe1 = Recipe.objects.get(id=res1.data['id'])
        recipe2 = Recipe.objects.get(id=res2.data['id'])

        self.assertEqual(recipe1.ingredients.count(), 2)
        self.assertEqual(recipe2.ingredients.count(), 2)

        for recipe in [recipe1, recipe2]:
            exists = recipe.ingredients.filter(
                name=ingredient_common['name']
            ).exists()
            self.assertTrue(exists)

        self.assertEqual(
            Ingredient.objects.filter(name=ingredient_common['name']).count(),
            2
        )

    def test_create_ingredient_on_update(self) -> None:
        """Test creating an ingredient when updating a recipe"""
        recipe = create_recipe()

        payload = {'ingredients': [{'name': 'Limes'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(name='Limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self) -> None:
        """Test clearing a recipe ingredients"""
        recipe = create_recipe()
        Ingredient.objects.create(
            name='Garlic',
            recipe=recipe
        )

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_recipes_by_name(self) -> None:
        """Test get a recipe with name filter"""
        create_recipe(name='Bacon Butty')
        payload = {'name': 'Baco'}

        res = self.client.get(RECIPES_URL, payload)

        recipes = Recipe.objects.filter(name__startswith=payload['name'])
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_error_get_nonexistant_recipe(self) -> None:
        """Test error when retrieving a nonexisting recipe"""
        res = self.client.get(f'{RECIPES_URL}100/')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_error_create_invalid_recipe(self) -> None:
        """Test error when creating and invalid recipe"""
        payload = {
            'description': 'Sample description Test',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_create_invalid_recipe_ingredients(self) -> None:
        """Test error when posting and invalid ingredient format"""
        payload = {
            'name': 'Sample recipe with Ingredients',
            'description': 'Sample description Test',
            'ingredients': 'ingredient 1',

        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
