from django.contrib import admin
from .models import Profile, Course, Workshop

# Register your models here.
admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Workshop)