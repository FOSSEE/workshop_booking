
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from recurrence.fields import RecurrenceField

position_choices = (
	("coordinator", "Coordinator"),
	("instructor", "Instructor")
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
                                in the format: '+929490956'.\
                                Up to 15 digits allowed.")
							)])
	position = models.CharField(max_length=32, choices=position_choices)
	is_email_verified = models.BooleanField(default=False)
	activation_key = models.CharField(max_length=40, blank=True, null=True)
	key_expiry_time = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return u"id: {0}| {1} {2} | {3} ".format(
											self.user.id,
											self.user.first_name, 
											self.user.last_name, 
											self.user.email
										    ) 


class WorkshopType(models.Model):
	""""Admin creates types of workshops which can be used by the instructor 
		to create workshops.
	"""

	workshoptype_name = models.CharField(max_length=120)
	workshoptype_description = models.TextField()
	workshoptype_duration = models.CharField(max_length=32, 
					help_text='Please write this in \
					following format eg: 3days, 8hours a day')

	def __str__(self):
		return u"{0} {1}".format(self.workshoptype_name, 
				self.workshoptype_duration
				)


class Workshop(models.Model):
	"""Instructor Creates workshop based on
	WorkshopTypes	available"""

	workshop_instructor = models.ForeignKey(User, on_delete=models.CASCADE)
	workshop_title = models.ForeignKey(
								WorkshopType, on_delete=models.CASCADE,
		 						help_text='Select the type of workshop.'
		 						)
	#For recurring workshops source: django-recurrence
	recurrences = RecurrenceField()

	def __str__(self):
		return u"{0} | {1} ".format(
					self.workshop_title, 
					self.workshop_instructor
					)


class RequestedWorkshop(models.Model):
	"""
	Contains Data of request for Workshops
	"""

	requested_workshop_instructor = models.ForeignKey(
											User,
											on_delete=models.CASCADE
											)
	requested_workshop_coordinator = models.ForeignKey(
								User, 
								related_name="%(app_label)s_%(class)s_related"
								)
	requested_workshop_date = models.DateField()
	status = models.CharField(
					max_length=32, default="Pending"
					)
	requested_workshop_title = models.ForeignKey(
							WorkshopType, 
							on_delete=models.CASCADE
							)


class ProposeWorkshopDate(models.Model):
	"""
		Contains details of proposed date and workshop from coordinator
	"""

	conditionone = models.BooleanField(default=False, help_text='I will give\
								minimum 50 participants for the workshop.')
	conditiontwo = models.BooleanField(default=False, help_text='I agree \
								that this booking won\'t be cancelled without \
								prior notice to the instructor and fossee.')
	conditionthree = models.BooleanField(default=False, help_text='This \
					proposal is subject to FOSSEE and instructor approval.')

	proposed_workshop_coordinator = models.ForeignKey(
										User, 
										on_delete=models.CASCADE
										)
	proposed_workshop_instructor = models.ForeignKey(User, null=True,
								related_name="%(app_label)s_%(class)s_related")

	proposed_workshop_title = models.ForeignKey(
								WorkshopType, on_delete=models.CASCADE,
		 						help_text='Select the type of workshop.'
		 						)

	proposed_workshop_date = models.DateField()

	status = models.CharField(
					max_length=32, default="Pending"
					)


class BookedWorkshop(models.Model):
	"""
	Contains details about Confirmed Booked/Completed Workshops
	"""

	booked_workshop_requested = models.ForeignKey(RequestedWorkshop, null=True) 
	booked_workshop_proposed = models.ForeignKey(ProposeWorkshopDate, null=True)
