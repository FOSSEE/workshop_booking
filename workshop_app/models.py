import os

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

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
)

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
)

states = (
    ("IN-AP", "Andhra Pradesh"),
    ("IN-AR", "Arunachal Pradesh"),
    ("IN-AS", "Assam"),
    ("IN-BR", "Bihar"),
    ("IN-CT", "Chhattisgarh"),
    ("IN-GA", "Goa"),
    ("IN-GJ", "Gujarat"),
    ("IN-HR", "Haryana"),
    ("IN-HP", "Himachal Pradesh"),
    ("IN-JK", "Jammu and Kashmir"),
    ("IN-JH", "Jharkhand"),
    ("IN-KA", "Karnataka"),
    ("IN-KL", "Kerala"),
    ("IN-MP", "Madhya Pradesh"),
    ("IN-MH", "Maharashtra"),
    ("IN-MN", "Manipur"),
    ("IN-ML", "Meghalaya"),
    ("IN-MZ", "Mizoram"),
    ("IN-NL", "Nagaland"),
    ("IN-OR", "Odisha"),
    ("IN-PB", "Punjab"),
    ("IN-RJ", "Rajasthan"),
    ("IN-SK", "Sikkim"),
    ("IN-TN", "Tamil Nadu"),
    ("IN-TG", "Telangana"),
    ("IN-TR", "Tripura"),
    ("IN-UT", "Uttarakhand"),
    ("IN-UP", "Uttar Pradesh"),
    ("IN-WB", "West Bengal"),
    ("IN-AN", "Andaman and Nicobar Islands"),
    ("IN-CH", "Chandigarh"),
    ("IN-DN", "Dadra and Nagar Haveli"),
    ("IN-DD", "Daman and Diu"),
    ("IN-DL", "Delhi"),
    ("IN-LD", "Lakshadweep"),
    ("IN-PY", "Puducherry")
)


def has_profile(user):
    """ check if user has profile """
    return True if hasattr(user, 'profile') else False


def attachments(instance, filename):
    return os.sep.join((instance.workshop_type.name.replace(" ", '_'), filename))


class Profile(models.Model):
    """Profile for users(instructors and coordinators)"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=32, blank=True, choices=title)
    institute = models.CharField(max_length=150)
    department = models.CharField(max_length=150, choices=department_choices)
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^.{10}$', message=(
                "Phone number must be entered \
                in the format: '9999999999'.\
                Up to 10 digits allowed.")
        )], null=False)
    position = models.CharField(max_length=32, choices=position_choices,
                                default='coordinator',
                                help_text='Select Coordinator if you want to organise a workshop\
         in your college/school. <br> Select Instructor if you want to conduct\
                 a workshop.')
    how_did_you_hear_about_us = models.CharField(max_length=255, blank=True, choices=source)
    location = models.CharField(max_length=255, blank=True, help_text="Place/City")
    state = models.CharField(max_length=255, choices=states, default="IN-MH")
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

    name = models.CharField(max_length=120)
    description = models.TextField()
    duration = models.CharField(max_length=32,
                                help_text='Please write this in \
                    following format eg: 3days, 8hours a day')
    terms_and_conditions = models.TextField()

    def __str__(self):
        return u"{0} {1}".format(self.name,
                                 self.duration
                                 )


class AttachmentFile(models.Model):
    attachments = models.FileField(upload_to=attachments, blank=True,
                                   help_text='Please upload workshop documents one by one, \
                        ie.workshop schedule, instructions etc. \
                        Please Note: Name of Schedule file should be similar to \
                        WorkshopType Name')
    workshop_type = models.ForeignKey(WorkshopType, on_delete=models.CASCADE)


class Workshop(models.Model):
    """
        Contains details of workshops
    """
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, null=True, related_name="%(app_label)s_%(class)s_related",
                                   on_delete=models.CASCADE)
    workshop_type = models.ForeignKey(WorkshopType, on_delete=models.CASCADE, help_text='Select the type of workshop.')
    date = models.DateField()
    STATUS_CHOICES = [(0, 'Pending'),
                      (1, 'Accepted'),
                      (2, 'Deleted')]

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    tnc_accepted = models.BooleanField(help_text="I accept the terms and conditions")

    def __str__(self):
        return u"{0} | {1} | {2} | {3} | {4}".format(
            self.date,
            self.workshop_type,
            self.coordinator,
            self.instructor,
            self.STATUS_CHOICES[self.status][1]
        )

    def get_status(self):
        return str(self.STATUS_CHOICES[self.status][1])


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


class ProfileComments(models.Model):
    """
    Contains comments posted by instructors on coordinator profile
    """

    coordinator = models.ForeignKey(User,
                                    on_delete=models.CASCADE)
    comment = models.TextField()
    instructor = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_related", on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return u"{0} | {1}".format(
            self.comment,
            self.created_date,
            self.coordinator,
            self.instructor
        )


class Banner(models.Model):
    """
    Add HTML for banner display on homepage
    """
    title = models.CharField(max_length=500)
    html = models.TextField()
    active = models.BooleanField()

    def __str__(self):
        return self.title
