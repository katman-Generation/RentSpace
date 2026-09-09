import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create the admin user from environment variables"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME")
        last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME")
        phone_number = os.environ.get("DJANGO_SUPERUSER_PHONE_NUMBER")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        required = {
            "DJANGO_SUPERUSER_EMAIL": email,
            "DJANGO_SUPERUSER_FIRST_NAME": first_name,
            "DJANGO_SUPERUSER_LAST_NAME": last_name,
            "DJANGO_SUPERUSER_PHONE_NUMBER": phone_number,
            "DJANGO_SUPERUSER_PASSWORD": password,
        }

        missing = [
            name for name, value in required.items()
            if not value
        ]

        if missing:
            raise ValueError(
                "Missing environment variables: "
                + ", ".join(missing)
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser created: {email}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser already exists: {email}"
                )
            )