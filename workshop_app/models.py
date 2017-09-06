
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from recurrence.fields import RecurrenceField
import os

position_choices = (
    ("coordinator", "Coordinator"),
    ("instructor", "Instructor")
    )

department_choices = (
    ("computer engineering", "Computer Science"),
    ("information technology", "Information Technology"),
    ("civil engineering", "Civil Engineering"),
    ("electrical engineering", "Electrical Engineering"),
    ("mechanical engineering", "Mechanical Engineering"),
    ("chemical engineering", "Chemical Engineering"),
    ("aerospace engineering", "Aerospace Engineering"),
    ("biosciences and bioengineering", "Biosciences and  BioEngineering"),
    ("electronics", "Electronics"),
    ("energy science and engineering", "Energy Science and Engineering"),
    ("others", "Others"),
    )

title = (
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
    ("Shriman", "Shri"),
    ("Shrimati", "Smt"),
    ("Kumari", "Ku"),
    ("Mr", "Mr."),
    ("Mrs", "Mrs."),
    ("Miss", "Ms."),
    ("other", "Other"),
    )

source = (
    ("FOSSEE Email", "FOSSEE Email"),
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
    ("Others", "Others"),
    )


def has_profile(user):
    """ check if user has profile """
    return True if hasattr(user, 'profile') else False

def attachments(instance, filename):
    return os.sep.join((instance.workshoptype_name.replace(" ", '_'), filename))

class Profile(models.Model):
    """Profile for users(instructors and coordinators)"""

    user = models.OneToOneField(User)
    title = models.CharField(max_length=32,blank=True, choices=title)
    institute = models.CharField(max_length=150)
    department = models.CharField(max_length=150, choices=department_choices)
    phone_number = models.CharField(
                max_length=10,
                validators=[RegexValidator(
                                regex=r'^.{10}$', message=(
                                "Phone number must be entered \
                                in the format: '9999999999'.\
                                Up to 10 digits allowed.")
                            )]
                ,null=False)
    position = models.CharField(max_length=32, choices=position_choices,
                    default='coordinator',
                    help_text='Select Coordinator if you want to organise a workshop\
                            in your college/school. <br> Select Instructor if you want to conduct\
                            a workshop.')
    source = models.CharField(max_length=255, blank=True,choices=source)
    location = models.CharField(max_length=255,blank=True, help_text="Place/City")
    is_email_verified = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, blank=True, null=True)
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
    workshoptype_attachments = models.FileField(upload_to=attachments, blank=True,
                    help_text='Please upload workshop documents one by one, \
                    ie.workshop schedule, instructions etc. \
                    Please Note: Name of Schedule file should be similar to \
                    WorkshopType Name')

    def __str__(self):
        return u"{0} {1}".format(self.workshoptype_name, 
                self.workshoptype_duration
                )


class Workshop(models.Model):
    """Instructor Creates workshop based on
    WorkshopTypes   available"""

    workshop_instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    workshop_title = models.ForeignKey(
                                WorkshopType, on_delete=models.CASCADE,
                                help_text=' [Select the type of workshop.] '
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

    def __str__(self):
        return u"{0} | {1} | {2}| {3}".format(
                    self.requested_workshop_date, 
                    self.requested_workshop_title,
                    self.requested_workshop_coordinator,
                    self.status
                    )

class ProposeWorkshopDate(models.Model):
    """
        Contains details of proposed date and workshop from coordinator
    """

    condition_one = models.BooleanField(default=False, help_text='We assure to\
     give minimum 50 participants for the workshop.')
    condition_two = models.BooleanField(default=False, help_text='We agree \
                                that this booking won\'t be cancelled without \
                                2days of prior notice to the instructor and fossee.')
    condition_three = models.BooleanField(default=False, help_text='This \
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

    def __str__(self):
        return u"{0} | {1} | {2}| {3}".format(
                    self.proposed_workshop_date, 
                    self.proposed_workshop_title,
                    self.proposed_workshop_coordinator,
                    self.status
                    )


class BookedWorkshop(models.Model):
    """
    Contains details about Confirmed Booked/Completed Workshops
    """

    booked_workshop_requested = models.ForeignKey(RequestedWorkshop, null=True) 
    booked_workshop_proposed = models.ForeignKey(ProposeWorkshopDate, null=True)

    def __str__(self):
        return u"{0} | {1} |".format(
                    self.booked_workshop_requested, 
                    self.booked_workshop_proposed
                    )

class Testimonial(models.Model):
    """
    Contains Testimonals of Workshops
    """

    name = models.CharField(max_length=150)
    institute = models.CharField(max_length=255)
    department = models.CharField(max_length=150)
    message = models.TextField()

    def __str__(self):
        return u"{0} | {1} ".format(
                    self.name, 
                    self.institute,
                    self.department
                    )
