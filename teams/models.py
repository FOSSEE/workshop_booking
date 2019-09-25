from django.db import models
from django.contrib.auth.models import User

from workshop_app.models import Profile

class Team(models.Model):
	members = models.ManyToManyField(Profile)
	creator = models.OneToOneField(User)
	created_date = models.DateTimeField(auto_now=True)