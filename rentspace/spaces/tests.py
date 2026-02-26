from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from spaces.models import Location, Space, SpaceType
from users.models import UserProfile


class SpaceApiTests(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(city="Harare", area="CBD")
        self.space_type = SpaceType.objects.create(name="Room")
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.viewer = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="StrongPass123!",
        )
        profile, _ = UserProfile.objects.get_or_create(user=self.owner)
        profile.phone_number = "+263771234567"
        profile.save()

        self.available_space = Space.objects.create(
            owner=self.owner,
            title="Available Space",
            description="A good space",
            price="300.00",
            space_type=self.space_type,
            location=self.location,
            is_available=True,
        )
        self.unavailable_space = Space.objects.create(
            owner=self.owner,
            title="Unavailable Space",
            description="Not available",
            price="450.00",
            space_type=self.space_type,
            location=self.location,
            is_available=False,
        )

    def test_space_list_only_shows_available(self):
        res = self.client.get("/api/spaces/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ids = [space["id"] for space in res.data]
        self.assertIn(self.available_space.id, ids)
        self.assertNotIn(self.unavailable_space.id, ids)

    def test_post_to_space_list_is_not_allowed(self):
        res = self.client.post("/api/spaces/", {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_space_requires_auth(self):
        res = self.client.post(
            "/api/spaces/create/",
            {
                "title": "New Space",
                "description": "desc",
                "price": "500.00",
                "location_id": self.location.id,
                "space_type_id": self.space_type.id,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_update_own_space(self):
        self.client.force_authenticate(user=self.owner)
        res = self.client.patch(
            f"/api/spaces/update/{self.available_space.id}/",
            {"title": "Updated Title"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.available_space.refresh_from_db()
        self.assertEqual(self.available_space.title, "Updated Title")

    def test_non_owner_cannot_update_other_users_space(self):
        self.client.force_authenticate(user=self.viewer)
        res = self.client.patch(
            f"/api/spaces/update/{self.available_space.id}/",
            {"title": "Should Fail"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_phone_hidden_for_unauthenticated_detail(self):
        res = self.client.get(f"/api/spaces/{self.available_space.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.data["owner_phone"])

    def test_owner_phone_shown_to_authenticated_user_in_detail(self):
        self.client.force_authenticate(user=self.viewer)
        res = self.client.get(f"/api/spaces/{self.available_space.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["owner_phone"], "+263771234567")
