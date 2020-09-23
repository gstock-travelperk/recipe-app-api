from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users APPI public"""

    def setUp(self):
        self.client = APIClient()

    def test_creat_valid_user_success(self):
        """Test creating user"""
        payload = {
            'email': 'test@gstock.com',
            'password': '123456',
            'name': 'Public User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test fails to create if already exists"""
        payload = {
            'email': 'test@gstock.com',
            'password': '123456',
            'name': 'Public User'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Tests that the password must be more than 5 characters"""

        payload = {
            'email': 'test@gstock.com',
            'password': '12',
            'name': 'Public User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertFalse(user_exists)
