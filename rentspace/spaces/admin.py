from django.contrib import admin
from .models import Space, SpaceType, Location, SpaceImage, Amenity, Category

# Register your models here.
admin.site.register(Space)
admin.site.register(SpaceType)
admin.site.register(Location)
admin.site.register(SpaceImage)
admin.site.register(Amenity)
admin.site.register(Category)