from django .conf import settings
from django.db import models

# Create your models here.
class Location(models.Model):
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.city} - {self.area}"
    
class SpaceType(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Space(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="spaces")
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    space_type = models.ForeignKey(SpaceType, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class SpaceImage(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="space_images/")
    