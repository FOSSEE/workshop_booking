import django
import os
import sys
import datetime as dt
from textwrap import dedent
from django.core.mail import send_mail
from time import sleep

#Setting Up Django Environment Using Existing settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workshop_portal.settings")
base_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
django.setup()
#Importing required email credentials
from workshop_portal.settings import (
                    EMAIL_HOST, 
                    EMAIL_PORT, 
                    EMAIL_HOST_USER, 
                    EMAIL_HOST_PASSWORD,
                    EMAIL_USE_TLS,
                    PRODUCTION_URL, 
                    SENDER_EMAIL,
                    ADMIN_EMAIL
                    )
from workshop_app.models import *
from datetime import datetime, date
class ReminderEmail():
	"""docstring for ReminderEmail"""

	def fetch(self):
		self.tomorrow = date.today() + dt.timedelta(days=3)
		self.upcoming_requested_workshops = RequestedWorkshop.objects.filter(
								requested_workshop_date=self.tomorrow, 
								status='ACCEPTED'
								)

		self.upcoming_proposed_workshops = ProposeWorkshopDate.objects.filter(
								proposed_workshop_date=self.tomorrow, 
								status='ACCEPTED'
								)

	def send_email(self):
		for w in self.upcoming_proposed_workshops:
			sleep(1)
			message = dedent("""\
					Dear {0}, 

					This is to remind you that
					you have a workshop on {1}, 
					for {2}.

					Create Course and Quiz for your workshop.

					Get in touch with your coordinator so that participants
					can be instructed for enrollment.

					Thank You.
					""".format(w.proposed_workshop_instructor.get_full_name(),
						w.proposed_workshop_date, w.proposed_workshop_title))
			send_mail(
				"Gentle Reminder about workshop on {0}"
				.format(w.proposed_workshop_date),message, SENDER_EMAIL,
				[w.proposed_workshop_instructor.email], fail_silently=False
				)

		for w in self.upcoming_requested_workshops:
			sleep(1)
			message = dedent("""\
					Dear {0}, 

					This is to remind you that
					you have a workshop on {1}, 
					for {2}.

					Create Course and Quiz for your workshop.

					Get in touch with your coordinator so that participants
					can be instructed for enrollment.

					Thank You.
					""".format(w.requested_workshop_instructor.get_full_name(),
						w.requested_workshop_date, w.requested_workshop_title))
			send_mail(
				"Gentle Reminder about workshop on {0}"
				.format(w.requested_workshop_date),message, SENDER_EMAIL,
				[w.requested_workshop_instructor.email], fail_silently=False
				)

if __name__ == '__main__':
	reminderObj = ReminderEmail()
	reminderObj.fetch()
	reminderObj.send_email()