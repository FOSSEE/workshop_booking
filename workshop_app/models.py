#from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

position_choices = (
	("student", "Student"),
	("instructor", "Instructor")
	)

class Profile(models.Model):
	"""Profile for users"""

	user = models.OneToOneField(User)
	institute = models.CharField(max_length=150)
	department = models.CharField(max_length=150)
	position = models.CharField(max_length=32, choices=position_choices)

	def __str__(self):
		return u"{0} {1} | {2}".format(self.user.first_name, self.user.last_name, self.user.email) 


def has_profile(user):
	""" check if user has profile """
	return True if hasattr(user, 'profile') else False

