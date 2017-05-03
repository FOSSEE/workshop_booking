__author__ = "Akshen Doke"

from django.core.mail import send_mail
from textwrap import dedent
from random import randint
import hashlib
from django.utils.crypto import get_random_string
from string import punctuation, digits
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters
from workshop_portal.settings import (
                    EMAIL_HOST, 
                    EMAIL_PORT, 
                    EMAIL_HOST_USER, 
                    EMAIL_HOST_PASSWORD,
                    EMAIL_USE_TLS
                    )

def generate_activation_key(username):
	"""Generates hashed secret key for email activation"""
	chars = letters + digits + punctuation
	secret_key = get_random_string(randint(10,40), chars)
	return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()

def send_smtp_email(request=None, subject=None, message=None,
				user_position=None, workshop_date=None,
				workshop_title=None, user_name=None,
				other_email=None, phone_number=None,
				institute=None, attachment=None):
	'''
		Send email using SMTPLIB
	'''

	from smtplib import SMTP
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.base import MIMEBase
	from email import encoders

	msg = MIMEMultipart()
	msg['From'] = EMAIL_HOST_USER
	msg['To'] = other_email
	msg['Subject'] = subject
	body = message
	msg.attach(MIMEText(body, 'plain'))

	if attachment:
		from django.conf import settings
		from os import listdir, path
		files = listdir(settings.MEDIA_ROOT)
		for f in files:
			print(path.join(settings.MEDIA_ROOT,f))
			attachment = open(path.join(settings.MEDIA_ROOT,f), 'rb')
			part = MIMEBase('application', 'octet-stream')
			part.set_payload((attachment).read())
			encoders.encode_base64(part)
			part.add_header('Content-Disposition', "attachment; filename= %s " % f)
			msg.attach(part)
	
	
	server = SMTP(EMAIL_HOST, EMAIL_PORT)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.esmtp_features['auth']='LOGIN DIGEST-MD5 PLAIN'
	server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
	text = msg.as_string()
	server.sendmail(EMAIL_HOST_USER, other_email, text)
	server.close()


def send_email(	request, call_on,
			user_position=None, workshop_date=None,
			workshop_title=None, user_name=None,
			other_email=None, phone_number=None,
			institute=None, key=None
			):
	'''
	Email sending function while registration and 
	booking confirmation.
	'''

	if call_on == "Registration":
		if user_position == "instructor":
			message = dedent("""\
					Your request as an Instructor at FOSSEE, IIT Bombay 
					has been received. Please click on the below link to 
					activate your account
					127.0.0.1/activate_user/{0}

					You will be notified via email on
					approval of your instructor account
					within 3 working days.

					In case of queries regarding the same revert to this 
					email.""".format(key))

			try:
				send_mail(
					"Instructor Registration - FOSSEE, IIT Bombay", message, 
					EMAIL_HOST_USER, [request.user.email], fail_silently=False
					)
			except Exception: 
				send_smtp_email(request=request, 
					subject="Instructor Registration - FOSSEE, IIT Bombay", 
					message=message, other_email=request.user.email,
					)
			

			#Send a mail to admin as well.
			message = dedent("""\	
					A new instructor request has been received.

					Instructor name:{0}
					Instructor email:{1}
					
					Please verify the profile and mail the user within 2
					working days.""".format(request.user, request.user.email))

			try:
				send_mail("New Instructor Registration - FOSSEE, IIT Bombay", 
					message, EMAIL_HOST_USER, ['workshops@fossee.in'], 
					fail_silently=False)
			except Exception:
				send_smtp_email(request=request, 
					subject="Instructor Registration - FOSSEE, IIT Bombay", 
					message=message, other_email='workshops@fossee.in',
					)
			
		else:
			message = dedent("""\
						Thank you for registering as a coordinator with us. 

						Your request as a coordinator has been accepted.
						Please click on the below link to 
						activate your account
						127.0.0.1/activate_user/{0}
						
						After activation you can proceed to book your dates for 
						the workshop(s).

						In case of queries regarding workshop booking(s), 
						revert to this email.""".format(key))

			try:
				send_mail(
					"Coordinator Registration at FOSSEE, IIT Bombay", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)
			except Exception:
				send_smtp_email(request=request, 
					subject="Coordinator Registration - FOSSEE, IIT Bombay", 
					message=message, other_email=request.user.email,
					)

	elif call_on == "Booking":
		if user_position == "instructor":
			message = dedent("""\
					Coordinator name:{0}
					Coordinator email: {1}
					Contact number:{2}
					Institute:{3}
					Workshop date:{4}
					Workshop title:{5}

					You may accept or reject this booking 
					workshop.fossee.in .""".format(
					user_name, request.user.email, 
					request.user.profile.phone_number,
					request.user.profile.institute,
					workshop_date, workshop_title
					))

			try:
				send_mail(
			 		"New FOSSEE Workshop booking on {0}".format(workshop_date),
			 		message, EMAIL_HOST_USER, [other_email], 
			 		fail_silently=False
			 		)
			except Exception:
				send_smtp_email(request=request, 
					subject="New FOSSEE Workshop booking on {0}"
					.format(workshop_date),
					message=message, other_email=other_email,
					)
		else:
			message = dedent("""\
					Thank You for New FOSSEE Workshop booking. 

					Workshop date:{0}
					Workshop title:{1}

					Your request has been received and is awaiting instructor 
					approval/disapproval. You will be notified about the status
					via email and on your workshops.fossee.in 

					In case of queries regarding workshop booking(s), revert
					to this email.""".format(
					workshop_date, workshop_title
					))

			try:
				send_mail(
					"Pending Request for New FOSSEE Workshop booking on {0}"
					.format(workshop_date), message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)
			except Exception:
				send_smtp_email(request=request, 
					subject="Pending Request for New FOSSEE Workshop booking \
					on {0}".format(workshop_date),
					message=message, other_email=request.user.email,
					)

	elif call_on == "Booking Confirmed":
		if user_position == "instructor":
			message = dedent("""\
			Coordinator name:{0}
			Coordinator email: {1}
			Contact number:{2}
			Institute:{3}
			Workshop date:{4}
			Workshop title:{5}

			You have accepted this booking.  Detailed instructions have
			been sent to the coordinator. """.format(user_name, user_name, 
				phone_number, institute, workshop_date, workshop_title))

			send_smtp_email(request=request, 
				subject="FOSSEE Workshop booking confirmation  on {0}".
				format(workshop_date), message=message,
				other_email=request.user.email, attachment=1
				)
		else:
			message = dedent("""\
				Instructor name:{0}
				Instructor email: {1}
				Contact number:{2}
				Workshop date:{3}
				Workshop title:{4}

				Your workshop booking has been accepted. Detailed 
				instructions are attached below.  

				In case of queries regarding the workshop 
				instructions/schedule revert to this email.""".format(
				request.user.username, request.user.email, 
				phone_number, workshop_date, workshop_title
				))

			send_smtp_email(request=request, 
				subject="FOSSEE Workshop booking confirmation  on {0}".
				format(workshop_date), message=message,
				other_email=other_email, attachment=1
				)

	elif call_on == "Booking Request Rejected":
		if user_position == "instructor":
			message = dedent("""\
					Coordinator name:{0}
					Coordinator email: {1}
					Contact number:{2}
					Institute:{3}
					Workshop date:{4}
					Workshop title:{4}

					You have rejected this booking.  The coordinator has
					been notified.""".format(user_name, other_email,
					phone_number, institute,
					workshop_date, workshop_title))

			try:
				send_mail("FOSSEE Workshop booking rejected for{0}"
					.format(workshop_date), message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False)
			except Exception:
				send_smtp_email(request=request, 
					subject="FOSSEE Workshop booking rejected for {0}".
					format(workshop_date), message=message,
					other_email=request.user.email
					)
		else:
			message = dedent("""\
					Workshop date:{0}
					Workshop title:{1}

					We regret to inform you that your workshop booking
					has been rejected due to unavailability of the
					instructor. You may try booking other available 
					slots workshops.fossee.in """
					.format(workshop_date, workshop_title))

			try:
				send_mail("FOSSEE Workshop booking rejected for {0}".
					format(workshop_date), message, EMAIL_HOST_USER, 
					[other_email], fail_silently=False)
			except Exception:
				send_smtp_email(request=request, 
					subject="FOSSEE Workshop booking rejected for {0}".
					format(workshop_date), message=message,
					other_email=other_email
					)

	elif call_on =='Workshop Deleted':
		message = dedent("""\
				You have deleted a Workshop.

				Workshop date:{0}
				Workshop title:{1}"""
				.format(workshop_date, workshop_title))
		try:
			send_mail("FOSSEE workshop deleted for {0}".format(workshop_date),
				message, EMAIL_HOST_USER, [request.user.email], 
				fail_silently=False)
		except Exception:
			send_smtp_email(request=request, 
				subject="FOSSEE Workshop deleted for {0}".
				format(workshop_date), message=message,
				other_email=request.user.email
				)
		
	else:
		message = "Issue at Workshop Booking App please check"
		try:
			send_mail("Issue At Workshop Booking App Mailing", message, EMAIL_HOST_USER,
				['doke.akshen@gmail.com', 'mahesh.p.gudi@gmail.com', 'aditya94palaparthy@gmail.com'], fail_silently=False)
		except Exception:
			send_smtp_email(request=request, 
				subject="Issue at Workshop Booking App please check",
				message=message, other_email='doke.akshen@gmail.com'
				)
