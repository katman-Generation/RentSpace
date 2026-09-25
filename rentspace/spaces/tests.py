import json
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from spaces.models import (
    Category,
    Location,
    Space,
    SpaceType,
    Institution,
    StudentAccommodation,
)

from users.models import UserProfile


User = get_user_model()


class SpaceApiTests(APITestCase):

    def setUp(self):
        # -------------------------
        # Rent Category
        # -------------------------
        self.category = Category.objects.create(
            name="Rent",
            slug="rent",
        )

        # -------------------------
        # Rent Space Type
        # -------------------------
        self.space_type = SpaceType.objects.create(
            name="Room",
            category=self.category,
        )

        # -------------------------
        # Student Category
        # -------------------------
        self.student_category = Category.objects.create(
            name="Student Accommodation",
            slug="student-accommodation",
        )

        # -------------------------
        # Student Space Type
        # -------------------------
        self.student_space_type = SpaceType.objects.create(
            name="Private Room",
            category=self.student_category,
        )

        # -------------------------
        # Location
        # -------------------------
        self.location = Location.objects.create(
            province="Harare",
            city="Harare",
            area="CBD",
        )

        # -------------------------
        # Users
        # -------------------------
        self.owner = User.objects.create_user(
            email="owner@example.com",
            first_name="Owner",
            last_name="User",
            phone_number="+263771234567",
            password="StrongPass123!",
        )

        self.viewer = User.objects.create_user(
            email="viewer@example.com",
            first_name="Viewer",
            last_name="User",
            phone_number="+263772345678",
            password="StrongPass123!",
        )

        # -------------------------
        # Owner profile
        # -------------------------
        profile, _ = UserProfile.objects.get_or_create(
            user=self.owner
        )

        profile.save()

        # -------------------------
        # Institution
        # -------------------------
        self.institution = Institution.objects.create(
            name="University of Zimbabwe",
            slug="university-of-zimbabwe",
            institution_type="university",
            city="Harare",
            campus="Main Campus",
        )

        # -------------------------
        # Available space
        # -------------------------
        self.available_space = Space.objects.create(
            owner=self.owner,
            title="Available Space",
            description="A good space",
            category=self.category,
            space_type=self.space_type,
            location=self.location,
            listing_purpose="rent",
            currency="USD",
            rental_period="month",
            price="300.00",
            is_available=True,
        )

        # -------------------------
        # Unavailable space
        # -------------------------
        self.unavailable_space = Space.objects.create(
            owner=self.owner,
            title="Unavailable Space",
            description="Not available",
            category=self.category,
            space_type=self.space_type,
            location=self.location,
            listing_purpose="rent",
            currency="USD",
            rental_period="month",
            price="450.00",
            is_available=False,
        )

    # ========================================================
    # EXISTING SPACE TESTS
    # ========================================================

    def test_space_list_only_shows_available(self):

        res = self.client.get(
            "/api/spaces/"
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        ids = [
            space["id"]
            for space in res.data
        ]

        self.assertIn(
            self.available_space.id,
            ids,
        )

        self.assertNotIn(
            self.unavailable_space.id,
            ids,
        )

    def test_post_to_space_list_is_not_allowed(self):

        res = self.client.post(
            "/api/spaces/",
            {},
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_create_space_requires_auth(self):

        res = self.client.post(
            "/api/spaces/create/",
            {
                "title": "New Space",
                "description": "desc",
                "price": "500.00",
                "location_id": self.location.id,
                "category_id": self.category.id,
                "space_type_id": self.space_type.id,
                "listing_purpose": "rent",
                "currency": "USD",
                "rental_period": "month",
            },
            format="multipart",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_owner_can_update_own_space(self):

        self.client.force_authenticate(
            user=self.owner
        )

        res = self.client.patch(
            f"/api/spaces/update/{self.available_space.id}/",
            {
                "title": "Updated Title"
            },
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.available_space.refresh_from_db()

        self.assertEqual(
            self.available_space.title,
            "Updated Title",
        )

    def test_non_owner_cannot_update_other_users_space(self):

        self.client.force_authenticate(
            user=self.viewer
        )

        res = self.client.patch(
            f"/api/spaces/update/{self.available_space.id}/",
            {
                "title": "Should Fail"
            },
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_owner_phone_hidden_for_unauthenticated_detail(self):

        res = self.client.get(
            f"/api/spaces/{self.available_space.id}/"
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertIsNone(
            res.data["owner_phone"]
        )

    def test_owner_phone_shown_to_authenticated_user_in_detail(self):

        self.client.force_authenticate(
            user=self.viewer
        )

        res = self.client.get(
            f"/api/spaces/{self.available_space.id}/"
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            res.data["owner_phone"],
            "+263771234567",
        )

    # ========================================================
    # STUDENT ACCOMMODATION TESTS
    # ========================================================

    def test_create_student_accommodation_listing(self):

        self.client.force_authenticate(
            user=self.owner
        )

        payload = {
            "title": "Private Student Room Near UZ",
            "description": "Clean furnished student room.",
            "category_id": self.student_category.id,
            "space_type_id": self.student_space_type.id,
            "location_id": self.location.id,
            "listing_purpose": "rent",
            "currency": "USD",
            "rental_period": "month",
            "price": "250.00",
            "deposit": "250.00",
            "bedrooms": 1,
            "bathrooms": 1,
            "furnished": True,
            "student_details": {
                "institution_id": self.institution.id,
                "campus": "Main Campus",
                "distance_to_campus_km": "1.20",
                "room_type": "private_room",
                "rooms_available": 3,
                "bathroom_type": "shared",
                "meal_plan": "optional",
            },
        }

        res = self.client.post(
            "/api/spaces/create/",
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
            res.data,
        )

        space = Space.objects.get(
            title="Private Student Room Near UZ"
        )

        self.assertEqual(
            space.owner,
            self.owner,
        )

        self.assertEqual(
            space.category,
            self.student_category,
        )

        self.assertEqual(
            space.space_type,
            self.student_space_type,
        )

        # ----------------------------------------------
        # Student accommodation should exist
        # ----------------------------------------------

        student_details = StudentAccommodation.objects.get(
            space=space
        )

        self.assertEqual(
            student_details.institution,
            self.institution,
        )

        self.assertEqual(
            student_details.campus,
            "Main Campus",
        )

        self.assertEqual(
            str(student_details.distance_to_campus_km),
            "1.20",
        )

        self.assertEqual(
            student_details.room_type,
            "private_room",
        )

        self.assertEqual(
            student_details.rooms_available,
            3,
        )

        self.assertEqual(
            student_details.bathroom_type,
            "shared",
        )

        self.assertEqual(
            student_details.meal_plan,
            "optional",
        )

        # ----------------------------------------------
        # Response should include student details
        # ----------------------------------------------

        self.assertIn(
            "student_details",
            res.data,
        )

        self.assertEqual(
            res.data["student_details"]["institution"]["name"],
            "University of Zimbabwe",
        )

        self.assertEqual(
            res.data["student_details"]["room_type"],
            "private_room",
        )

    def test_student_listing_requires_student_details(self):

        self.client.force_authenticate(
            user=self.owner
        )

        payload = {
            "title": "Student Room Without Details",
            "description": "Missing student information.",
            "category_id": self.student_category.id,
            "space_type_id": self.student_space_type.id,
            "location_id": self.location.id,
            "listing_purpose": "rent",
            "currency": "USD",
            "rental_period": "month",
            "price": "250.00",
        }

        res = self.client.post(
            "/api/spaces/create/",
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "student_details",
            res.data,
        )

    def test_normal_rent_listing_cannot_have_student_details(self):

        self.client.force_authenticate(
            user=self.owner
        )

        payload = {
            "title": "Normal Rental Room",
            "description": "Normal rental listing.",
            "category_id": self.category.id,
            "space_type_id": self.space_type.id,
            "location_id": self.location.id,
            "listing_purpose": "rent",
            "currency": "USD",
            "rental_period": "month",
            "price": "300.00",
            "student_details": {
                "institution_id": self.institution.id,
                "campus": "Main Campus",
                "distance_to_campus_km": "1.00",
                "room_type": "private_room",
                "rooms_available": 1,
                "bathroom_type": "shared",
                "meal_plan": "none",
            },
        }

        res = self.client.post(
            "/api/spaces/create/",
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "student_details",
            res.data,
        )
        
    def test_create_student_accommodation_multipart(self):

        self.client.force_authenticate(
            user=self.owner
        )

        payload = {
            "title": "Multipart Student Room",
            "description": "Student listing submitted as multipart.",
            "category_id": self.student_category.id,
            "space_type_id": self.student_space_type.id,
            "location_id": self.location.id,
            "listing_purpose": "rent",
            "currency": "USD",
            "rental_period": "month",
            "price": "275.00",
            "student_details": json.dumps({
                "institution_id": self.institution.id,
                "campus": "Main Campus",
                "distance_to_campus_km": "2.50",
                "room_type": "private_room",
                "rooms_available": 2,
                "bathroom_type": "shared",
                "meal_plan": "none",
            }),
        }

        res = self.client.post(
            "/api/spaces/create/",
            payload,
            format="multipart",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
            res.data,
        )

        space = Space.objects.get(
            title="Multipart Student Room"
        )

        student_details = StudentAccommodation.objects.get(
            space=space
        )

        self.assertEqual(
            student_details.institution,
            self.institution,
        )

        self.assertEqual(
            student_details.room_type,
            "private_room",
        )

        self.assertEqual(
            student_details.rooms_available,
            2,
        )