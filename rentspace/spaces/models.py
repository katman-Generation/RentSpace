from django.conf import settings
from django.db import models
from django.utils.text import slugify


# ============================================================
# LOCATION
# ============================================================

class Location(models.Model):
    province = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100
    )

    area = models.CharField(
        max_length=100
    )

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

    class Meta:
        ordering = ["province", "city", "area"]
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["area"]),
            models.Index(fields=["province"]),
        ]

    def __str__(self):
        return f"{self.city} - {self.area}"


# ============================================================
# CATEGORY
# ============================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ============================================================
# SPACE TYPES
# ============================================================

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

    class Meta:
        ordering = ["category", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"],
                name="unique_space_type_per_category"
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# ============================================================
# AMENITIES
# ============================================================

class Amenity(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================
# INSTITUTIONS
# Used primarily by Student Accommodation
# ============================================================

class Institution(models.Model):

    INSTITUTION_TYPE_CHOICES = [
        ("university", "University"),
        ("college", "College"),
        ("polytechnic", "Polytechnic"),
        ("institute", "Institute"),
        ("other", "Other"),
    ]

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    institution_type = models.CharField(
        max_length=20,
        choices=INSTITUTION_TYPE_CHOICES,
        default="university"
    )

    city = models.CharField(
        max_length=100
    )

    campus = models.CharField(
        max_length=150,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

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

    class Meta:
        ordering = ["name"]

        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["institution_type"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        if self.campus:
            return f"{self.name} - {self.campus}"

        return self.name


# ============================================================
# SPACE
# Main property/listing model
# ============================================================

class Space(models.Model):

    # --------------------------------------------------------
    # Ownership
    # --------------------------------------------------------

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="spaces"
    )

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Buy / Rent
    # --------------------------------------------------------

    LISTING_PURPOSE_CHOICES = [
        ("rent", "For Rent"),
        ("sale", "For Sale"),
    ]

    listing_purpose = models.CharField(
        max_length=10,
        choices=LISTING_PURPOSE_CHOICES,
        default="rent"
    )

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    CURRENCY_CHOICES = [
        ("USD", "US Dollar"),
        ("ZiG", "Zimbabwe Gold"),
    ]

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD"
    )

    # --------------------------------------------------------
    # Rental information
    # --------------------------------------------------------

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
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    available_from = models.DateField(
        null=True,
        blank=True
    )

    is_available = models.BooleanField(
        default=True
    )

    # --------------------------------------------------------
    # Property information
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Amenities
    # --------------------------------------------------------

    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="spaces"
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    VERIFICATION_STATUS_CHOICES = [
        ("unverified", "Unverified"),
        ("pending", "Verification Pending"),
        ("verified", "Verified"),
        ("rejected", "Verification Rejected"),
    ]

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="unverified"
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_spaces"
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["space_type"]),
            models.Index(fields=["location"]),
            models.Index(fields=["listing_purpose"]),
            models.Index(fields=["is_available"]),
            models.Index(fields=["verification_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


# ============================================================
# STUDENT ACCOMMODATION
# Only used when a Space belongs to Student Accommodation
# ============================================================

class StudentAccommodation(models.Model):

    ROOM_TYPE_CHOICES = [
        ("private_room", "Private Room"),
        ("shared_room", "Shared Room"),
        ("entire_unit", "Entire Unit"),
    ]

    BATHROOM_TYPE_CHOICES = [
        ("private", "Private Bathroom"),
        ("shared", "Shared Bathroom"),
    ]

    MEAL_PLAN_CHOICES = [
        ("none", "No Meals"),
        ("optional", "Meals Available"),
        ("included", "Meals Included"),
    ]

    space = models.OneToOneField(
        Space,
        on_delete=models.CASCADE,
        related_name="student_details"
    )

    institution = models.ForeignKey(
        Institution,
        on_delete=models.PROTECT,
        related_name="student_accommodations"
    )

    campus = models.CharField(
        max_length=150,
        blank=True
    )

    distance_to_campus_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default="private_room"
    )

    rooms_available = models.PositiveIntegerField(
        default=1
    )

    bathroom_type = models.CharField(
        max_length=10,
        choices=BATHROOM_TYPE_CHOICES,
        null=True,
        blank=True
    )

    meal_plan = models.CharField(
        max_length=10,
        choices=MEAL_PLAN_CHOICES,
        default="none"
    )

    class Meta:
        verbose_name = "Student Accommodation"
        verbose_name_plural = "Student Accommodations"

        indexes = [
            models.Index(fields=["institution"]),
            models.Index(fields=["room_type"]),
            models.Index(fields=["distance_to_campus_km"]),
        ]

    def __str__(self):
        return f"Student accommodation - {self.space.title}"


# ============================================================
# SPACE IMAGES
# ============================================================

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