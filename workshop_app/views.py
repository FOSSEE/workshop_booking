from .forms import (
					UserRegistrationForm, UserLoginForm, 
					ProfileForm, CreateWorkshop,
					ProposeWorkshopDateForm
					)
from .models import (
					Profile, User,
					has_profile, Workshop, 
					WorkshopType, RequestedWorkshop,
					BookedWorkshop, ProposeWorkshopDate
					)
from django.template import RequestContext
from datetime import datetime, date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.utils import timezone
from collections import OrderedDict
from dateutil.parser import parse
from .send_mails import send_email
from django.http import HttpResponse, HttpResponseRedirect
from textwrap import dedent

__author__ = "Akshen Doke"
__credits__ = ["Mahesh Gudi", "Aditya P.", "Ankit Javalkar",
                "Prathamesh Salunke", "Akshen Doke", "Kiran Kishore",
                "KhushalSingh Rajput"]


def is_email_checked(user):
	if hasattr(user, 'profile'):
		return True if user.profile.is_email_verified else False
	else:
		return False


def index(request):
	'''Landing Page'''

	user = request.user
	form = UserLoginForm()
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/workshop_booking/manage/')
		return redirect('/workshop_booking/book/')
	elif request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data
			login(request, user)
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/workshop_booking/manage/')
			return redirect('/workshop_booking/book/')
		
	return render(request, "workshop_app/index.html", {"form": form})


def is_instructor(user):
	'''Check if the user is having instructor rights'''
	return True if user.groups.filter(name='instructor').count() > 0 else False
		

def user_login(request):
	'''User Login'''
	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/workshop_booking/manage/')
		return redirect('/workshop_booking/book/')

	if request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data
			login(request, user)
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/workshop_booking/manage/')
			return redirect('/workshop_booking/book/')
		else:
			return render(request, 'workshop_app/login.html', {"form": form})
	else:
		form = UserLoginForm()
		return render(request, 'workshop_app/login.html', {"form": form})


def user_logout(request):
	'''Logout'''
	logout(request)
	return render(request, 'workshop_app/logout.html')


def activate_user(request, key):
	try:
		user = Profile.objects.get(activation_key=key)	
	except:
		return redirect('/workshop_booking/register/')

	if user.is_email_verified:
		status = "Your email is already verified"
	elif timezone.now() > user.key_expiry_time:
		status = "Your activation has expired please register again"
		Profile.objects.get(user_id=user.user_id).delete()
		User.objects.get(id=user.user_id).delete()
		return render(request, 'workshop_app/activation.html',
					{"status": status})
	elif key == user.activation_key:
		user.is_email_verified = True
		user.save()
		status = "Your account has been activated"
	else:
		logout(request)
		return redirect('/workshop_booking/logout/')
	return render(request, 'workshop_app/activation.html',
				{"status": status})


def user_register(request):
	'''User Registeration form'''
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			username, password, key = form.save()
			new_user = authenticate(username=username, password=password)
			login(request, new_user)
			user_position = request.user.profile.position
			send_email(
					   request, call_on='Registration', 
					   user_position=user_position,
					   key=key
					  )
			
			return render(request, 'workshop_app/activation.html')
		else:
			return render(
						request, "workshop_app/register.html", 
						{"form": form}
						)
	else:
		form = UserRegistrationForm()
	return render(request, "workshop_app/register.html", {"form": form})


#This is shown to coordinator for booking workshops
def book(request):
	user = request.user
	if user.is_authenticated():
		if is_email_checked(user):
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/workshop_booking/manage/')

			workshop_details = Workshop.objects.all()
			
			workshop_occurence_list = []

			for workshops in workshop_details:
				dates = workshops.recurrences.between(
					datetime(2017, 3, 12, 0, 0, 0),
		    		datetime(2040, 12, 31, 0, 0, 0), #Needs to be changed yearly
		    		inc=True
					)
				
				for d in range(len(dates)):
					workshop_occurence = [
										dates[d].strftime("%d-%m-%Y"),
										workshops.workshop_instructor,
				 						workshops.workshop_title,
				 						workshops.workshop_instructor_id,
				 						workshops.workshop_title_id,
				 						workshops.workshop_title.workshoptype_description
					 					]
					
					workshop_occurence_list.append(workshop_occurence)
					del workshop_occurence
			
			#Gives you the objects of BookedWorkshop
			bookedworkshop = BookedWorkshop.objects.all()
			if len(bookedworkshop) != 0:
				for b in bookedworkshop:
					'''
					handles objects from bookedworkshop 
						-requested
						-proposed
					'''
					try:
						x = b.booked_workshop_requested.requested_workshop_date.strftime("%d-%m-%Y")
						y = b.booked_workshop_requested.requested_workshop_title
					except:
						x = b.booked_workshop_proposed.proposed_workshop_date.strftime("%d-%m-%Y")
						y = b.booked_workshop_proposed.proposed_workshop_title
					for a in workshop_occurence_list:
						if a[0] == x and a[2] == y:
							workshop_occurence_list.remove(a)
					del x, y

			#Objects of RequestedWorkshop for that particular coordinator
			rW_obj = RequestedWorkshop.objects.filter(
									requested_workshop_coordinator=request.user
									)
			for r in rW_obj:
				x = r.requested_workshop_date.strftime("%d-%m-%Y")
				for a in workshop_occurence_list:
					if a[0] == x:
						workshop_occurence_list.remove(a)
				del x
	 

			#Show upto 12 Workshops per page
			paginator = Paginator(workshop_occurence_list, 12) 
			page = request.GET.get('page')
			try:
				workshop_occurences  = paginator.page(page)
			except PageNotAnInteger:
			#If page is not an integer, deliver first page.
				workshop_occurences  = paginator.page(1)
			except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
				workshop_occurences  = paginator.page(paginator.num_pages)

			return render(
						request, "workshop_app/booking.html",
						{"workshop_details": workshop_occurences}
						 )
		else:
			return render(request, "workshop_app/activation.html")
	else:
		return redirect('/workshop_booking/login/')


@login_required
def book_workshop(request):
	'''
	Function for Updating RequestedWorkshop Model
	'''
	if request.method == 'POST':
		user_position = request.user.profile.position
		client_data = request.body.decode("utf-8").split("&")
		client_data = client_data[0].split("%2C")
		workshop_date = client_data[0][2:]

		if client_data[-1] == '0':
			queue = RequestedWorkshop.objects.filter(
				requested_workshop_instructor=client_data[1],
				requested_workshop_date=datetime.strptime(
											client_data[0][2:], "%d-%m-%Y"
											),
				requested_workshop_title=client_data[-2]
				).count() + 1

			return HttpResponse(str(queue))

		workshops_list = Workshop.objects.filter(
										workshop_instructor=client_data[1],
										workshop_title_id=client_data[2]
										)

		for workshop in workshops_list:
			workshop_recurrence_list =  workshop.recurrences.between(
										datetime(2017, 3, 12, 0, 0, 0),
										datetime(2040, 12, 31, 0, 0, 0),
										inc=True
										)

			rW_obj = RequestedWorkshop()
			if	RequestedWorkshop.objects.filter(
					requested_workshop_instructor=workshop.workshop_instructor,
					requested_workshop_date=datetime.strptime(
											client_data[0][2:], "%d-%m-%Y",
											),
					requested_workshop_coordinator=request.user,
					requested_workshop_title=client_data[-1]
					).count() > 0:

					return HttpResponse(dedent("""You already have a booking 
								for this workshop please check the 
								instructors response in My Workshops tab and
								also check your email."""))
			else:
				for w in workshop_recurrence_list:
					if workshop_date == (w.strftime("%d-%m-%Y")):
						rW_obj.requested_workshop_instructor = workshop.workshop_instructor
						rW_obj.requested_workshop_coordinator = request.user
						rW_obj.requested_workshop_date = datetime.strptime(
													   workshop_date,"%d-%m-%Y"
														)
						rW_obj.requested_workshop_title = workshop.workshop_title
						rW_obj.save()

						queue = RequestedWorkshop.objects.filter(
								requested_workshop_instructor=workshop.workshop_instructor,
								requested_workshop_date=datetime.strptime(
											workshop_date, "%d-%m-%Y",
											),
								requested_workshop_title=client_data[-1]
								).count()

						# Mail to instructor
						send_email(request, call_on='Booking', 
									   user_position='instructor', 
									   workshop_date=workshop_date,
									   workshop_title=workshop.workshop_title.workshoptype_name,
									   user_name=str(request.user),
									   other_email=workshop.workshop_instructor.email
									   )
						phone_number = workshop.workshop_instructor.profile.phone_number
						#Mail to coordinator
						send_email(request, call_on='Booking',
							workshop_date=workshop_date,
							workshop_title=workshop.workshop_title.workshoptype_name,
							user_name=workshop.workshop_instructor.username,
							other_email=workshop.workshop_instructor.email,
							phone_number=phone_number)
								
						return HttpResponse(dedent("""\
						Thank You, Please check 
						your email for further information. Your number on the
						queue for this book is {0}""".format(str(queue))))
	else:
		return HttpResponse("Some Error Occurred.")


@login_required
def manage(request):
	user = request.user
	if user.is_authenticated() and is_email_checked(user):
		#Move user to the group via admin
		if user.groups.filter(name='instructor').count() > 0:
			try:
				#Can Handle Multiple Workshops
				workshop_details = Workshop.objects.filter(
													workshop_instructor=user.id
													)

				workshop_occurence_list = []
				for workshop in workshop_details:
					workshop_occurence = workshop.recurrences.between(
												datetime(2017, 3, 12, 0, 0, 0),
												datetime(2040, 12, 31, 0, 0, 0),
												inc=True													
												)
					for i in range(len(workshop_occurence)):

						workshop_occurence_list.append({ 
										"user": str(user), 
										"workshop": workshop.workshop_title, 
										"date": workshop_occurence[i].date()
										})
					
				requested_workshop = RequestedWorkshop.objects.filter(
											requested_workshop_instructor=user.id
											)
				
				
				#Need to recheck logic
				for j in range(len(requested_workshop)):
					for i in workshop_occurence_list:
						a = requested_workshop[j].requested_workshop_date
						b = requested_workshop[j].requested_workshop_title
						if i['date'] == a and i['workshop'] == b:
							workshop_occurence_list.remove(i)
						del a, b

				
				#Show upto 12 Workshops per page
				paginator = Paginator(workshop_occurence_list, 12)
				page = request.GET.get('page')
				try:
					workshops  = paginator.page(page)
				except PageNotAnInteger:
				#If page is not an integer, deliver first page.
					workshops  = paginator.page(1)
				except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
					workshops  = paginator.page(paginator.num_pages)
			except:
				workshops = None
			
			return render(
						request, "workshop_app/manage.html", 
						{"workshop_occurence_list": workshops}
						)

		return redirect('/workshop_booking/book/')
	else:
		return redirect('/workshop_booking/login/')


@login_required
def my_workshops(request):
	user = request.user

	if user.is_authenticated() and is_email_checked(user):
		if is_instructor(user):
			if request.method == 'POST':
				user_position = request.user.profile.position
				client_data = request.body.decode("utf-8").split("&")
				client_data = client_data[0].split("%2C")

				if client_data[-1] == 'ACCEPTED':
					workshop_date = datetime.strptime(
										client_data[1], "%Y-%m-%d"
										)

					coordinator_obj = User.objects.get(username=client_data[0][2:])

					workshop_status = RequestedWorkshop.objects.get(
									requested_workshop_instructor=user.id,
									requested_workshop_date=workshop_date,
									requested_workshop_coordinator=coordinator_obj.id,
									requested_workshop_title=client_data[2]
									)

					workshop_status.status = client_data[-1]
					workshop_status.save()
					booked_workshop_obj = BookedWorkshop()
					booked_workshop_obj.booked_workshop_requested = workshop_status
					booked_workshop_obj.save()

					cmail = workshop_status.requested_workshop_coordinator.email
					cname = workshop_status.requested_workshop_coordinator.username
					cnum = workshop_status.requested_workshop_coordinator.profile.phone_number
					cinstitute = workshop_status.requested_workshop_coordinator.profile.institute
					inum = request.user.profile.phone_number
					wtitle = workshop_status.requested_workshop_title.workshoptype_name

					#For Instructor
					send_email(request, call_on='Booking Confirmed', 
						user_position='instructor', 
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						user_name=str(cname),
						other_email=cmail,
						phone_number=cnum,
						institute=cinstitute
						)

					#For Coordinator
					send_email(request, call_on='Booking Confirmed',  
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						other_email=cmail,
						phone_number=inum
						)

				elif client_data[-1] == 'DELETED':
					workshop_date = client_data[1]
					workshops_list = Workshop.objects.filter(workshop_instructor=request.user.id,
											workshop_title_id=client_data[2]
											)
					
					for workshop in workshops_list:
						workshop_recurrence_list = workshop.recurrences.between(
													datetime(2017, 3, 12, 0, 0, 0),
													datetime(2040, 12, 31, 0, 0, 0),
													inc=True
													)

						for d in workshop_recurrence_list:
							if workshop_date == d.strftime("%Y-%m-%d"):
								rW_obj = RequestedWorkshop()
								rW_obj.requested_workshop_instructor = request.user
								rW_obj.requested_workshop_coordinator = request.user
								rW_obj.requested_workshop_date = workshop_date
								rW_obj.requested_workshop_title = workshop.workshop_title
								rW_obj.status = client_data[-1]
								rW_obj.save()
								bW_obj = BookedWorkshop()
								bW_obj.booked_workshop_requested = rW_obj
								bW_obj.save()

					#For instructor
					send_email(request, call_on='Workshop Deleted',
						workshop_date=str(client_data[1]),
						workshop_title=workshop.workshop_title
						)

					return HttpResponse("Workshop Deleted")
				
				elif client_data[-1] == 'APPROVED':
					print(client_data)
					workshop_date = datetime.strptime(
										client_data[1], "%Y-%m-%d"
										)

					coordinator_obj = User.objects.get(username=client_data[0][2:])
					workshop_status = ProposeWorkshopDate.objects.get(
									proposed_workshop_date=workshop_date,
									proposed_workshop_coordinator=coordinator_obj.id,
									proposed_workshop_title=client_data[2]
									)

					workshop_status.status = 'ACCEPTED'
					workshop_status.proposed_workshop_instructor = user
					workshop_status.save()
					booked_workshop_obj = BookedWorkshop()
					booked_workshop_obj.booked_workshop_proposed = workshop_status
					booked_workshop_obj.save()

					cmail = workshop_status.proposed_workshop_coordinator.email
					cname = workshop_status.proposed_workshop_coordinator.username
					cnum = workshop_status.proposed_workshop_coordinator.profile.phone_number
					cinstitute = workshop_status.proposed_workshop_coordinator.profile.institute
					inum = request.user.profile.phone_number
					wtitle = workshop_status.proposed_workshop_title.workshoptype_name

					#For Instructor
					send_email(request, call_on='Booking Confirmed', 
						user_position='instructor', 
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						user_name=str(cname),
						other_email=cmail,
						phone_number=cnum,
						institute=cinstitute
						)

					#For Coordinator
					send_email(request, call_on='Booking Confirmed',  
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						other_email=cmail,
						phone_number=inum
						)

				else:
					workshop_date = datetime.strptime(
										client_data[1], "%Y-%m-%d"
										)
					coordinator_obj = User.objects.get(username=client_data[0][2:])
					workshop_status = RequestedWorkshop.objects.get(
										requested_workshop_instructor=user.id,
										requested_workshop_date=workshop_date,
										requested_workshop_coordinator=coordinator_obj.id,
										requested_workshop_title=client_data[2]
										)
					workshop_status.status = client_data[-1]
					workshop_status.save()

					wtitle = workshop_status.requested_workshop_title.workshoptype_name
					cmail = workshop_status.requested_workshop_coordinator.email
					cname = workshop_status.requested_workshop_coordinator.username
					cnum = workshop_status.requested_workshop_coordinator.profile.phone_number
					cinstitute = workshop_status.requested_workshop_coordinator.profile.institute

					#For Instructor
					send_email(request, call_on='Booking Request Rejected', 
						user_position='instructor', 
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						user_name=str(cname),
						other_email=cmail,
						phone_number=cnum,
						institute=cinstitute
						)

					#For Coordinator
					send_email(request, call_on='Booking Request Rejected',
						workshop_date=str(client_data[1]),
						workshop_title=wtitle,
						other_email=cmail
						)

			workshops = []
			workshop_occurence_list = RequestedWorkshop.objects.filter(
									requested_workshop_instructor=user.id
									)
			for w in workshop_occurence_list:
				workshops.append(w)

			proposed_workshop = ProposeWorkshopDate.objects.filter(
							proposed_workshop_instructor=user.id
							)
			for p in proposed_workshop:
				workshops.append(p)

			proposed_workshop_pending  = ProposeWorkshopDate.objects.filter(
									status='Pending'
									)
			for p in proposed_workshop_pending:
				workshops.append(p)

			#Show upto 12 Workshops per page
			paginator = Paginator(workshops, 12)
			page = request.GET.get('page')
			try:
				workshop_occurences = paginator.page(page)
			except PageNotAnInteger:
			#If page is not an integer, deliver first page.
				workshop_occurences = paginator.page(1)
			except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
				workshop_occurences = paginator.page(paginator.num_pages)
			return render(request, 'workshop_app/my_workshops.html',
				{ "workshop_occurences" :workshop_occurences})

		else:
			workshops = []
			workshop_occurence_list = RequestedWorkshop.objects.filter(
						requested_workshop_coordinator=user.id
						)
			for w in workshop_occurence_list:
				workshops.append(w)

			proposed_workshop = ProposeWorkshopDate.objects.filter(
				proposed_workshop_coordinator=user.id
				)
			for p in proposed_workshop:
				workshops.append(p)			

			#Show upto 12 Workshops per page
			paginator = Paginator(workshops, 12)
			page = request.GET.get('page')
			try:
				workshop_occurences = paginator.page(page)
			except PageNotAnInteger:
			#If page is not an integer, deliver first page.
				workshop_occurences = paginator.page(1)
			except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
				workshop_occurences = paginator.page(paginator.num_pages)
			return render(request, 'workshop_app/my_workshops.html',
				{"workshop_occurences": workshop_occurences})
	else:
		return redirect('/workshop_booking/login/')


@login_required
def propose_workshop(request):
	'''Coordinator proposed a workshop and date'''

	user = request.user
	if is_email_checked(user):
		if is_instructor(user):
			return redirect('/workshop_booking/manage/')
		else:
			if request.method == 'POST':
				form = ProposeWorkshopDateForm(request.POST)
				if form.is_valid():
					form_data = form.save(commit=False)
					form_data.proposed_workshop_coordinator = user
					form_data.proposed_workshop_coordinator.save()
					form_data.save()
					return redirect('/workshop_booking/my_workshops/')
			else:
				form = ProposeWorkshopDateForm()
			return render(
						request, 'workshop_app/propose_workshop.html',
						{"form": form }
						)
	else:
		return render(request, 'workshop_app/activation.html')

@login_required
def view_profile(request):
	""" view instructor and coordinator profile """
	return render(request, "workshop_app/view_profile.html")


@login_required
def edit_profile(request):
	""" edit profile details facility for instructor and coordinator """

	user = request.user
	if is_instructor(user) and is_email_checked(user):
		template = 'workshop_app/manage.html'
	else:
		if is_email_checked(user):
			template = 'workshop_app/booking.html'
	context = {'template': template}
	if has_profile(user) and is_email_checked(user):
		profile = Profile.objects.get(user_id=user.id)
	else:
		profile = None

	if request.method == 'POST':
		form = ProfileForm(request.POST, user=user, instance=profile)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.user = user
			form_data.user.first_name = request.POST['first_name']
			form_data.user.last_name = request.POST['last_name']
			form_data.user.save()
			form_data.save()

			return render(
						request, 'workshop_app/profile_updated.html', 
						context
						)
		else:
			context['form'] = form
			return render(request, 'workshop_app/edit_profile.html', context)
	else:
		form = ProfileForm(user=user, instance=profile)
		context['form'] = form
		return render(request, 'workshop_app/edit_profile.html', context)


@login_required
def create_workshop(request):
	'''Instructor creates workshops'''

	user = request.user
	if is_instructor(user) and is_email_checked(user):
		if request.method == 'POST':
			form = CreateWorkshop(request.POST)
			if form.is_valid():
				form_data = form.save(commit=False)
				#form_data.profile_id = profile.id
				form_data.workshop_instructor = user
				form_data.workshop_instructor.save()
				form_data.save()
				return redirect('/workshop_booking/manage/')
		else:
			form = CreateWorkshop()
		return render(
					 request, 'workshop_app/create_workshop.html',
					 {"form": form }
					 )
	else:
		return redirect('/workshop_booking/book/')


@login_required
def view_workshoptype_list(request):
	'''Gives the types of workshop details '''
	user = request.user
	if is_email_checked(user):
		workshoptype_list = WorkshopType.objects.all()

		paginator = Paginator(workshoptype_list, 12) #Show upto 12 workshops per page

		page = request.GET.get('page')
		try:
			workshoptype = paginator.page(page)
		except PageNotAnInteger:
			#If page is not an integer, deliver first page.
			workshoptype = paginator.page(1)
		except EmptyPage:
			#If page is out of range(e.g 999999), deliver last page.
			workshoptype = paginator.page(paginator.num_pages)

		return render(
				request, 'workshop_app/view_workshoptype_list.html', \
				{'workshoptype': workshoptype}
				)
	else:
		return redirect('/workshop_booking/activate_user/')


def view_workshoptype_details(request):
	'''Gives the details for types of workshops.'''
	workshoptype_list = WorkshopType.objects.all()

	paginator = Paginator(workshoptype_list, 12) #Show upto 12 workshops per page

	page = request.GET.get('page')
	try:
		workshoptype = paginator.page(page)
	except PageNotAnInteger:
		#If page is not an integer, deliver first page.
		workshoptype = paginator.page(1)
	except EmptyPage:
		#If page is out of range(e.g 999999), deliver last page.
		workshoptype = paginator.page(paginator.num_pages)

	return render(
			request, 'workshop_app/view_workshoptype_details.html', \
				{'workshoptype': workshoptype}
				)
	

def benefits(request):
	return render(request, 'workshop_app/view_benefits.html')

def faq(request):
	return render(request, 'workshop_app/view_faq.html')

def how_to_participate(request):
	return render(request, 'workshop_app/how_to_participate.html')