from django.contrib import admin
from .models import Space, SpaceType, Location, SpaceImage

# Register your models here.
admin.site.register(Space)
admin.site.register(SpaceType)
admin.site.register(Location)
admin.site.register(SpaceImage)