#from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from recurrence.fields import RecurrenceField

position_choices = (
	("coordinator", "Coordinator"),
	("instructor", "Instructor")
	)

status_choices = (
	("pending", "Pending"),
	("confirm", "Confirm")
	)

def has_profile(user):
	""" check if user has profile """
	return True if hasattr(user, 'profile') else False

class Profile(models.Model):
	"""Profile for users(instructors and coordinators)"""

	user = models.OneToOneField(User)
	institute = models.CharField(max_length=150)
	department = models.CharField(max_length=150)
	phone_number = models.CharField(
				max_length=15,
				validators=[RegexValidator(
									regex=r'^\+?1?\d{9,15}$', message=(
									"Phone number must be entered \
                                     in the format: '+999999999'.\
                                      Up to 15 digits allowed.")
							)])
	position = models.CharField(max_length=32, choices=position_choices)

	def __str__(self):
		return u"id: {0}| {1} {2} | {3} ".format(
											self.user.id,
											self.user.first_name, 
											self.user.last_name, 
											self.user.email
										    ) 


class Course(models.Model):
	""""Admin creates courses which can be used by the instructor 
		to create workshops.
	"""

	course_name = models.CharField(max_length=120)
	course_description = models.TextField()
	course_duration = models.CharField(max_length=12)

	def __str__(self):
		return u"{0} {1}".format(self.course_name, self.course_duration)


class Workshop(models.Model):
	"""Instructor Creates workshop based on
	Courses	available"""

	workshop_instructor = models.ForeignKey(User, on_delete=models.CASCADE)
	workshop_title = models.ForeignKey(
										Course, on_delete=models.CASCADE,\
		 								help_text='Select the course you \
		 								would like to create a workshop for'
		 							  )
	
	recurrences = RecurrenceField()
	#status = models.BooleanField() Book, Pending, Booked

	def __str__(self):
		return u"{0} | {1} ".format(self.workshop_title, self.workshop_instructor)


# class completed_Workshop(models.Model):
# 	"""
# 	Contains Data of Booked/Completed Workshops 
# 	"""

# 	workshop_instructor = models.ForeignKey(User, on_delete=models.CASCADE)
# 	workshop_coordinator = models.ForeignKey(User)
# 	status = models.CharField(max_length=32, choices=status_choices)
# 	workshop_title = models.ForeignKey(Course, on_delete=models.CASCADE)



