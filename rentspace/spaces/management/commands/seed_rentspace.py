from django.core.management.base import BaseCommand

from spaces.models import (
    Category,
    SpaceType,
    Amenity,
    Institution,
)


class Command(BaseCommand):
    help = "Seed RentSpace categories, property types, amenities and institutions"

    CATEGORY_DATA = {
        "Buy": {
            "description": "Properties and land available for purchase.",
            "types": [
                "House",
                "Flat / Apartment",
                "Townhouse / Cluster",
                "Cottage / Garden Flat",
                "Stand / Residential Land",
                "Commercial Property",
                "Office",
                "Warehouse / Factory",
                "Shop / Retail",
                "Farm / Agricultural Land",
            ],
        },

        "Rent": {
            "description": "Properties and spaces available for rent.",
            "types": [
                "House",
                "Flat / Apartment",
                "Townhouse / Cluster",
                "Cottage / Garden Flat",
                "Room",
                "Commercial Property",
                "Office",
                "Warehouse / Factory",
                "Shop / Retail",
            ],
        },

        "Student Accommodation": {
            "description": "Accommodation designed for students.",
            "types": [
                "Student House",
                "Private Room",
                "Shared Room",
                "Student Flat / Apartment",
            ],
        },
    }

    AMENITIES = [
        "Wi-Fi",
        "Water",
        "Electricity",
        "Solar",
        "Backup Power",
        "Borehole",
        "Security",
        "CCTV",
        "Gated",
        "Parking",
        "Garage",
        "Carport",
        "Garden",
        "Swimming Pool",
        "Furnished",
    ]

    # --------------------------------------------------------
    # Zimbabwe institutions
    # --------------------------------------------------------

    INSTITUTION_DATA = [
        {
            "name": "University of Zimbabwe",
            "institution_type": "university",
            "city": "Harare",
            "campus": "Main Campus",
        },
        {
            "name": "Harare Institute of Technology",
            "institution_type": "institute",
            "city": "Harare",
            "campus": "Main Campus",
        },
        {
            "name": "Women's University in Africa",
            "institution_type": "university",
            "city": "Harare",
            "campus": "Main Campus",
        },
        {
            "name": "Zimbabwe Ezekiel Guti University",
            "institution_type": "university",
            "city": "Bindura",
            "campus": "Main Campus",
        },
        {
            "name": "Bindura University of Science Education",
            "institution_type": "university",
            "city": "Bindura",
            "campus": "Main Campus",
        },
        {
            "name": "Chinhoyi University of Technology",
            "institution_type": "university",
            "city": "Chinhoyi",
            "campus": "Main Campus",
        },
        {
            "name": "Midlands State University",
            "institution_type": "university",
            "city": "Gweru",
            "campus": "Main Campus",
        },
        {
            "name": "National University of Science and Technology",
            "institution_type": "university",
            "city": "Bulawayo",
            "campus": "Main Campus",
        },
        {
            "name": "Lupane State University",
            "institution_type": "university",
            "city": "Lupane",
            "campus": "Main Campus",
        },
        {
            "name": "Great Zimbabwe University",
            "institution_type": "university",
            "city": "Masvingo",
            "campus": "Main Campus",
        },
        {
            "name": "Africa University",
            "institution_type": "university",
            "city": "Mutare",
            "campus": "Main Campus",
        },
        {
            "name": "Catholic University of Zimbabwe",
            "institution_type": "university",
            "city": "Harare",
            "campus": "Main Campus",
        },
        {
            "name": "Reformed Church University",
            "institution_type": "university",
            "city": "Masvingo",
            "campus": "Main Campus",
        },
        {
            "name": "Zimbabwe Open University",
            "institution_type": "university",
            "city": "Harare",
            "campus": "Main Campus",
        },
    ]

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding RentSpace..."
            )
        )

        # --------------------------------------------------
        # Categories and Space Types
        # --------------------------------------------------

        for category_name, category_data in self.CATEGORY_DATA.items():

            category, category_created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "description": category_data["description"]
                }
            )

            # Update description if the category already exists.
            if category.description != category_data["description"]:
                category.description = category_data["description"]
                category.save(update_fields=["description"])

            if category_created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created category: {category.name}"
                    )
                )
            else:
                self.stdout.write(
                    f"Category already exists: {category.name}"
                )

            # ----------------------------------------------
            # Space Types
            # ----------------------------------------------

            for type_name in category_data["types"]:

                space_type, created = SpaceType.objects.get_or_create(
                    category=category,
                    name=type_name
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Created type: {type_name}"
                        )
                    )

        # --------------------------------------------------
        # Amenities
        # --------------------------------------------------

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding amenities..."
            )
        )

        for amenity_name in self.AMENITIES:

            amenity, created = Amenity.objects.get_or_create(
                name=amenity_name
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created amenity: {amenity_name}"
                    )
                )

        # --------------------------------------------------
        # Institutions
        # --------------------------------------------------

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Seeding institutions..."
            )
        )

        for institution_data in self.INSTITUTION_DATA:

            institution, created = Institution.objects.get_or_create(
                name=institution_data["name"],
                defaults=institution_data,
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created institution: {institution.name}"
                    )
                )

            else:

                updated = False

                for field, value in institution_data.items():

                    if getattr(institution, field) != value:

                        setattr(
                            institution,
                            field,
                            value
                        )

                        updated = True

                if updated:

                    institution.save()

                    self.stdout.write(
                        f"Updated institution: {institution.name}"
                    )

                else:

                    self.stdout.write(
                        f"Institution already exists: {institution.name}"
                    )

        # --------------------------------------------------
        # Complete
        # --------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "\nRentSpace seed completed successfully."
            )
        )