__author__ = "Akshen Doke"

from django.core.mail import send_mail
from textwrap import dedent
from workshop_portal.settings import (
                    EMAIL_HOST, 
                    EMAIL_PORT, 
                    EMAIL_HOST_USER, 
                    EMAIL_HOST_PASSWORD,
                    EMAIL_USE_TLS
                    )

def send_email(request, call_on,
				user_position=None, workshop_date=None,
				workshop_title=None, user_name=None,
				other_email=None, phone_number=None
				):
	'''
	Email sending function while registration and 
	booking confirmation.
	'''

	if call_on == "Registration":
		if user_position == "instructor":
			message = dedent("""\
						Thank You for Registering on this platform.
						Since you have ask for Instructor Profile,
						we will get back to you soon after verifying your
						profile.
						In case if you don\t get any response within 3days, 
						Please contact us at workshops@fossee.in""")
			send_mail(
					"Welcome to FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)

			#Send a mail to admin as well as a notification.
			message = dedent("""\	
						There is a Request for instructor profile on Workshop
						Booking Website from {0} Please get check the profile 
						and get back to the user within 2days.
						""".format(request.user))
			send_mail("Instructor Request", message, EMAIL_HOST_USER,
				['workshops@fossee.in'], fail_silently=False)
			
		else:
			message = dedent("""\
						Thank You for Registering on this platform.
						If you face any issue during your session please
						contact us a workshops@fossee.in""")
			send_mail(
					"Welcome to FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)

	elif call_on == "Booking":
		if user_position == "instructor":
			message = dedent("""\
				You got a workshop booking request from user:{0}, email:{1}, 
				phone_number:{2} for workshop_title:{3} on date:{4}
				please respond at the earliest""".format(
					user_name, request.user.email, 
					request.user.profile.phone_number,
					workshop_title, workshop_date
					)
				)
			send_mail(
					"Python Workshop Booking | FOSSEE", message, EMAIL_HOST_USER, 
					[other_email], fail_silently=False
					)
		else:
			message = dedent("""\
					Thank You for Booking on this platform.
					Here are your workshop details workshop_title:{0} 
					workshop_date:{1}, instructor_email:{2}, 
					instructor phone_number:{3} 
					If you face any issue during your session please contact
					respective instructor or fossee at workshops@fossee.in""".format(
											workshop_title, workshop_date,
											other_email, phone_number
											)
					)
			send_mail(
					"Python Workshop Booking | FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)

	elif call_on == "Booking Confirmed":
		if user_position == "instructor":
			message = dedent("""\
				You have confirmed the booking on workshop_date:{0} for 
				workshop_title:{1} by coordinator:{2} coordinator_email:{3},
				coordinator_phone_number:{4}"""
				.format(workshop_date, workshop_title, user_name, other_email,
					phone_number))
			send_mail("Python Workshop Booking Confirmation", message, EMAIL_HOST_USER,
				[request.user.email], fail_silently=False)
		else:
			message = dedent("""\
						Your workshop on {0} for {1} has been confirmed by the
						instructor please get in touch with the
						instructor {2} - {3} for further assistance""".format(
						workshop_date, workshop_title,
						request.user.email, phone_number))
			send_mail("Python Workshop Booking Confirmation", message, EMAIL_HOST_USER,
				[other_email], fail_silently=False)

	elif call_on == "Booking Request Rejected":
		if user_position == "instructor":
			message = dedent("""\
						You have reject the booking on {0} for {1} by {2}"""
						.format(workshop_date, workshop_title, user_name))
			send_mail("Python Workshop Booking Rejected", message, 
				EMAIL_HOST_USER, [request.user.email], fail_silently=False)
		else:
			message = dedent("""\
							Your workshop request on {0}
							has been rejected by the instructor,
							please try for some other day.""".format(workshop_date))
			send_mail("Python Workshop Booking Request Rejected", message, 
				EMAIL_HOST_USER, [other_email], fail_silently=False)

	elif call_on =='Workshop Deleted':
		message = dedent("""\
						You have deleted a Workshop, scheduled on {0},
						workshop title: {1}"""
						.format(workshop_date, workshop_title)) 
		send_mail("Python Workshop Deleted", message, EMAIL_HOST_USER,
			[request.user.email], fail_silently=False)
		
	else:
		message = "Issue at Workshop Booking App please check"
		send_mail("Issue At Workshop Booking App Mailing", message, EMAIL_HOST_USER,
				[doke.akshen@gmail.com, mahesh.p.gudi@gmail.com, aditya94palaparthy@gmail.com], fail_silently=False)
