from django.contrib import admin
from .models import (
				Profile, WorkshopType, 
				Workshop, ProposeWorkshopDate,
				RequestedWorkshop)

# Register your models here.
admin.site.register(Profile)
admin.site.register(WorkshopType)
admin.site.register(Workshop)
admin.site.register(ProposeWorkshopDate)
admin.site.register(RequestedWorkshop)
