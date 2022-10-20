"""
Tests for recipe API
"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

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
        create_recipe()
        create_recipe()

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
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
