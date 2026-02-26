from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def test_register_then_login_returns_tokens(self):
        register_res = self.client.post(
            "/api/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(register_res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

        login_res = self.client.post(
            "/api/login/",
            {"username": "newuser", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_res.data)
        self.assertIn("refresh", login_res.data)

    def test_profile_requires_authentication(self):
        res = self.client.get("/api/profile/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_with_jwt(self):
        user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )

        login_res = self.client.post(
            "/api/login/",
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        patch_res = self.client.patch(
            "/api/profile/",
            {"phone_number": "+263771111111"},
            format="json",
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["phone_number"], "+263771111111")
