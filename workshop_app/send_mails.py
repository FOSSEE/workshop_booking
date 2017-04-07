from django.core.mail import send_mail
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
				other_email=None
				):
	'''
	Email sending function while registration and 
	booking confirmation.
	'''

	if call_on == "Registration":
		if user_position == "instructor":
			message = "Thank You for Registering on this platform. \n \
						Since you have ask for Instructor Profile, \n \
						we will get back to you soon after verifying your \n \
						profile. \
						In case if you don\t get any response within 3days, \
						Please contact us at   "
			send_mail(
					"Welcome to FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)
			#Send a mail to admin as well as a notification.
		else:
			message = "Thank You for Registering on this platform.\n \
						Rules. \n \ If you face any issue during \
						 your session please contact fossee."
			send_mail(
					"Welcome to FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)

	elif call_on == "Booking":
		if user_position == "instructor":
			message = "You got a workshop booking request from "+user_name+" for "+workshop_title+" on "+workshop_date+" please respond."
			send_mail(
					"Python Workshop Booking | FOSSEE", message, EMAIL_HOST_USER, 
					[other_email], fail_silently=False
					)

		else:
			message = "Thank You for Booking on this platform.\
					Here are your workshop details " +workshop_title+ "\
					If you face any issue during your session please contact \
					fossee."
			send_mail(
					"Python Workshop Booking | FOSSEE", message, EMAIL_HOST_USER, 
					[request.user.email], fail_silently=False
					)

	elif call_on == "Booking Confirmed":
		if user_position == "instructor":
			message = "You have confirmed the booking"
			send_mail("Python Workshop Booking Confirmation", message, EMAIL_HOST_USER,
				[request.user.email], fail_silently=False)
		else:
			message = "Your workshop for "+workshop_date+"request has been confirmed"
			send_mail("Python Workshop Booking Confirmation", message, EMAIL_HOST_USER,
				[other_email], fail_silently=False)

	elif call_on == "Booking Request Rejected":
		if user_position == "instructor":
			message = "You have reject the booking on "+workshop_date+" for "+workshop_title
			send_mail("Python Workshop Booking Rejected", message, EMAIL_HOST_USER,
				[request.user.email], fail_silently=False)
		else:
			message = "Your workshop request for "+workshop_date+" has been cancelled please \
			try for some other day."
			send_mail("Python Workshop Booking Request Rejected", message, EMAIL_HOST_USER,
				[other_email], fail_silently=False)

	else:
		message = "Issue at Workshop Booking App please check"
		send_mail("Issue At Workshop Booking App", message, EMAIL_HOST_USER,
				[doke.akshen@gmail.com, mahesh.p.gudi@gmail.com, aditya94palaparthy@gmail.com], fail_silently=False)
