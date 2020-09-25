from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """
    Test the public available tags Apis
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PirvateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user('test@gstock.com',
                                                         'pass1234')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desserts')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        other_user = get_user_model().objects.create_user('other@gstock.com',
                                                          'otherpass')
        Tag.objects.create(user=other_user, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {'name': 'testag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload['name']).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
