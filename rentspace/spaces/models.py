from django.conf import settings
from django.db import models

# Create your models here.
class Location(models.Model):
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.city} - {self.area}"
    

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class SpaceType(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="space_types"
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name

class Amenity(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name
    

class Space(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spaces"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="spaces"
    )

    space_type = models.ForeignKey(
        SpaceType,
        on_delete=models.PROTECT,
        related_name="spaces"
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="spaces"
    )
    RENTAL_PERIOD_CHOICES = [
        ("hour", "Per Hour"),
        ("day", "Per Day"),
        ("week", "Per Week"),
        ("month", "Per Month"),
        ("year", "Per Year"),
    ]

    rental_period = models.CharField(
        max_length=20,
        choices=RENTAL_PERIOD_CHOICES,
        default="month"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    available_from = models.DateField(
        null=True,
        blank=True
    )

    is_available = models.BooleanField(
        default=True
    )

    bedrooms = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    bathrooms = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    parking_spaces = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    floor_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    furnished = models.BooleanField(
        null=True,
        blank=True
    )

    capacity = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="spaces"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


    
class SpaceImage(models.Model):
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="space_images/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Image for {self.space.title}"
    