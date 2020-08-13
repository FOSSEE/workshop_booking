from django.db import models
from django.contrib.auth.models import User

from workshop_app.models import Profile

class Team(models.Model):
    members = models.ManyToManyField(Profile)
    creator = models.OneToOneField(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Team created by {self.creator.get_full_name()}"
