from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthFlowTests(APITestCase):

    def test_register_then_login_returns_tokens(self):
        register_res = self.client.post(
            "/api/register/",
            {
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "phone_number": "+263773333333",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            register_res.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email="newuser@example.com"
            ).exists()
        )

        login_res = self.client.post(
            "/api/login/",
            {
                "email": "newuser@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            login_res.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            login_res.data,
        )

        self.assertIn(
            "refresh",
            login_res.data,
        )

    def test_profile_requires_authentication(self):
        res = self.client.get(
            "/api/profile/"
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_update_with_jwt(self):
        user = User.objects.create_user(
            email="owner@example.com",
            first_name="Owner",
            last_name="User",
            phone_number="+263771234567",
            password="StrongPass123!",
        )

        login_res = self.client.post(
            "/api/login/",
            {
                "email": "owner@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(
            login_res.status_code,
            status.HTTP_200_OK,
        )

        token = login_res.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        patch_res = self.client.patch(
            "/api/profile/",
            {
                "phone_number": "+263771111111"
            },
            format="json",
        )

        self.assertEqual(
            patch_res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            patch_res.data["phone_number"],
            "+263771111111",
        )