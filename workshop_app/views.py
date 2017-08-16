from .forms import (
					UserRegistrationForm, UserLoginForm, 
					ProfileForm, CreateWorkshop,
					ProposeWorkshopDateForm
					)
from .models import (
					Profile, User,
					has_profile, Workshop, 
					WorkshopType, RequestedWorkshop,
					BookedWorkshop, ProposeWorkshopDate,
					Testimonial
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
from django.conf import settings
from os import listdir, path, sep
from zipfile import ZipFile
import datetime as dt
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io

__author__ = "Akshen Doke"
__credits__ = ["Mahesh Gudi", "Aditya P.", "Ankit Javalkar",
                "Prathamesh Salunke", "Kiran Kishore",
                "KhushalSingh Rajput", "Prabhu Ramachandran",
                "Arun KP"]


def is_email_checked(user):
	if hasattr(user, 'profile'):
		return True if user.profile.is_email_verified else False
	else:
		return False


def index(request):
	'''Landing Page'''

	user = request.user
	form = UserLoginForm()
	if user.is_authenticated() and is_email_checked(user):
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/manage/')
		return redirect('/book/')
	elif request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data
			login(request, user)
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/manage/')
			return redirect('/book/')
		
	return render(request, "workshop_app/index.html", {"form": form})


def is_instructor(user):
	'''Check if the user is having instructor rights'''
	return True if user.groups.filter(name='instructor').count() > 0 else False
		

def user_login(request):
	'''User Login'''
	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/manage/')
		return redirect('/book/')

	if request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data
			login(request, user)
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/manage/')
			return redirect('/book/')
		else:
			return render(request, 'workshop_app/login.html', {"form": form})
	else:
		form = UserLoginForm()
		return render(request, 'workshop_app/login.html', {"form": form})


def user_logout(request):
	'''Logout'''
	logout(request)
	return render(request, 'workshop_app/logout.html')


def activate_user(request, key=None):
	user = request.user
	if key is None:
		if user.is_authenticated() and user.profile.is_email_verified==0 and \
		timezone.now() > user.profile.key_expiry_time:
			status = "1"
			Profile.objects.get(user_id=user.profile.user_id).delete()
			User.objects.get(id=user.profile.user_id).delete()
			return render(request, 'workshop_app/activation.html', 
						{'status':status})
		elif user.is_authenticated() and user.profile.is_email_verified==0:
			return render(request, 'workshop_app/activation.html')
		elif user.is_authenticated() and user.profile.is_email_verified:
			status = "2"
			return render(request, 'workshop_app/activation.html', 
						{'status':status})
		else:
			return redirect('/register/')

	try:
		user = Profile.objects.get(activation_key=key)	
	except:
		return redirect('/register/')
		
	if key == user.activation_key:
		user.is_email_verified = True
		user.save()
		status = "0"
	else:
		logout(request)
		return redirect('/logout/')
	return render(request, 'workshop_app/activation.html',
				{"status": status})


def user_register(request):
	'''User Registration form'''
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
			if request.user.is_authenticated():
				return redirect('/view_profile/')
			return render(
						request, "workshop_app/registration/register.html", 
						{"form": form}
						)
	else:
		if request.user.is_authenticated() and is_email_checked(request.user):
			return redirect('/my_workshops/')
		elif request.user.is_authenticated():
			return render(request, 'workshop_app/activation.html') 
		form = UserRegistrationForm()
	return render(request, "workshop_app/registration/register.html", {"form": form})


#This is shown to coordinator for booking workshops
def book(request):
	user = request.user
	if user.is_authenticated():
		if is_email_checked(user):
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/manage/')

			workshop_details = Workshop.objects.all()
			
			workshop_occurence_list = []
			today = datetime.now() + dt.timedelta(days=3)
			upto = datetime.now() + dt.timedelta(weeks=52)
			for workshops in workshop_details:
				dates = workshops.recurrences.between(
					today,
		    		upto,
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
			return redirect('/activate_user/')
	else:
		return redirect('/login/')


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
		today = datetime.now() + dt.timedelta(days=3)
		upto = datetime.now() + dt.timedelta(weeks=52)
		for workshop in workshops_list:
			workshop_recurrence_list =  workshop.recurrences.between(
										today,
										upto,
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
									   user_name=str(request.user.get_full_name()),
									   other_email=workshop.workshop_instructor.email
									   )
						phone_number = workshop.workshop_instructor.profile.phone_number
						#Mail to coordinator
						send_email(request, call_on='Booking',
							workshop_date=workshop_date,
							workshop_title=workshop.workshop_title.workshoptype_name,
							user_name=workshop.workshop_instructor.profile.user.get_full_name(),
							other_email=workshop.workshop_instructor.email,
							phone_number=phone_number)
								
						return HttpResponse(dedent("""\
						Your request has been successful, Please check 
						your email for further information. Your request is number
						{0} in the queue.""".format(str(queue))))
	else:
		logout(request)
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
				today = datetime.now() + dt.timedelta(days=3)
				upto = datetime.now() + dt.timedelta(weeks=52)
				for workshop in workshop_details:
					workshop_occurence = workshop.recurrences.between(
												today,
												upto,
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

		return redirect('/book/')
	else:
		return redirect('/activate_user/')


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
					ws = workshop_status
					cmail = ws.requested_workshop_coordinator.email
					cname = ws.requested_workshop_coordinator.profile.user.get_full_name()
					cnum = ws.requested_workshop_coordinator.profile.phone_number
					cinstitute = ws.requested_workshop_coordinator.profile.institute
					inum = request.user.profile.phone_number
					wtitle = ws.requested_workshop_title.workshoptype_name

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
					
					today = datetime.now() + dt.timedelta(days=3)
					upto = datetime.now() + dt.timedelta(weeks=52)
					for workshop in workshops_list:
						workshop_recurrence_list = workshop.recurrences.between(
													today,
													upto,
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
					ws = workshop_status
					cmail = ws.proposed_workshop_coordinator.email
					cname = ws.proposed_workshop_coordinator.profile.user.get_full_name()
					cnum = ws.proposed_workshop_coordinator.profile.phone_number
					cinstitute = ws.proposed_workshop_coordinator.profile.institute
					inum = request.user.profile.phone_number
					wtitle = ws.proposed_workshop_title.workshoptype_name

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
					ws = workshop_status
					wtitle = ws.requested_workshop_title.workshoptype_name
					cmail = ws.requested_workshop_coordinator.email
					cname = ws.requested_workshop_coordinator.profile.user.get_full_name()
					cnum = ws.requested_workshop_coordinator.profile.phone_number
					cinstitute = ws.requested_workshop_coordinator.profile.institute

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
			paginator = Paginator(workshops[::-1], 12)
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
			paginator = Paginator(workshops[::-1], 12)
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
		return redirect('/login/')


@login_required
def propose_workshop(request):
	'''Coordinator proposed a workshop and date'''

	user = request.user
	if is_email_checked(user):
		if is_instructor(user):
			return redirect('/manage/')
		else:
			if request.method == 'POST':
				form = ProposeWorkshopDateForm(request.POST)
				if form.is_valid():
					form_data = form.save(commit=False)
					form_data.proposed_workshop_coordinator = user
					#Avoiding Duplicate workshop entries for same date and workshop_title
					if ProposeWorkshopDate.objects.filter(
						proposed_workshop_date=form_data.proposed_workshop_date,
						proposed_workshop_title=form_data.proposed_workshop_title,
						proposed_workshop_coordinator=form_data.proposed_workshop_coordinator
						).exists():
						return redirect('/my_workshops/')
					else:
						form_data.proposed_workshop_coordinator.save()
						form_data.save()
						instructors = Profile.objects.filter(position='instructor')
						for i in instructors:
							send_email(request, call_on='Proposed Workshop',
									user_position='instructor',
									workshop_date=str(form_data.proposed_workshop_date),
									workshop_title=form_data.proposed_workshop_title,
									user_name=str(user.get_full_name()),
									other_email=i.user.email,
									phone_number=user.profile.phone_number,
									institute=user.profile.institute
									)
						return redirect('/my_workshops/')
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
	user = request.user
	if is_email_checked(user) and user.is_authenticated():
		return render(request, "workshop_app/view_profile.html")
	else:
		if user.is_authenticated():
			return render(request, 'workshop_app/activation.html')
		else:
			try:
				logout(request)
				return redirect('/login/')
			except:
				return redirect('/register/')


@login_required
def edit_profile(request):
	""" edit profile details facility for instructor and coordinator """

	user = request.user
	if is_email_checked(user):
		if is_instructor(user):
			template = 'workshop_app/manage.html'
		else:
			template = 'workshop_app/booking.html'
	else:
		try:
			logout(request)
			return redirect('/login/')
		except:
			return redirect('/register/')

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
						request, 'workshop_app/profile_updated.html'
						)
		else:
			context['form'] = form
			return render(request, 'workshop_app/edit_profile.html', context)
	else:
		form = ProfileForm(user=user, instance=profile)
		return render(request, 'workshop_app/edit_profile.html', {'form':form})


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
				return redirect('/manage/')
		else:
			form = CreateWorkshop()
		return render(
					 request, 'workshop_app/create_workshop.html',
					 {"form": form }
					 )
	else:
		return redirect('/book/')


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
		return redirect('/activate_user/')


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

def file_view(request, workshop_title):
	if workshop_title =='flowchart':
		pdf_file = open(path.join(settings.MEDIA_ROOT,'flowchart.pdf'), 'rb')
		return HttpResponse(pdf_file, content_type="application/pdf")
	else:
		filename = WorkshopType.objects.get(id=workshop_title)
		attachment_path = path.dirname(filename.workshoptype_attachments.path)
		zipfile_name = string_io()
		zipfile = ZipFile(zipfile_name, "w")
		attachments = listdir(attachment_path)
		for file in attachments:
			file_path = sep.join((attachment_path, file))
			zipfile.write(file_path, path.basename(file_path))
		zipfile.close()
		zipfile_name.seek(0)
		response = HttpResponse(content_type='application/zip')
		response['Content-Disposition'] = 'attachment; filename={0}.zip'.format(
			filename.workshoptype_name.replace(" ", "_")
	        )
		response.write(zipfile_name.read())
		return response

def testimonials(request):
	testimonials = Testimonial.objects.all().order_by('-id')
	paginator = Paginator(testimonials, 3) #Show upto 12 workshops per page

	page = request.GET.get('page')
	try:
		messages = paginator.page(page)
	except PageNotAnInteger:
		#If page is not an integer, deliver first page.
		messages = paginator.page(1)
	except EmptyPage:
		#If page is out of range(e.g 999999), deliver last page.
		messages = paginator.page(paginator.num_pages)
	return render(request, 'workshop_app/testimonals.html', {"messages":messages})

@login_required
def scheduled_workshops(request):
	user = request.user
	today = datetime.now()
	upto = datetime.now() + dt.timedelta(days=15)
	if is_instructor(user) and is_email_checked(user):
		try:
			#Fetches Accepted workshops which were proposed by Coordinators
			proposed_workshops = ProposeWorkshopDate.objects.filter(
								proposed_workshop_date__range=(today, upto),
								status='ACCEPTED'
								)
			proposed_workshops = (sorted(proposed_workshops,
								key=lambda x: datetime.strftime(
								x.proposed_workshop_date, '%d-%m-%Y'
								)))
			#Fetches Accepted workshops which were Accepted by Instructors based on their Availability
			requested_workshops = RequestedWorkshop.objects.filter(
								requested_workshop_date__range=(today, upto),
								status='ACCEPTED'
								)
			requested_workshops = (sorted(requested_workshops,
								key=lambda x: datetime.strftime(
								x.request_workshop_date, '%d-%m-%Y'
								)))
			
		except:
			proposed_workshops = None
			requested_workshops = None
		return render(request, 'workshop_app/scheduled_workshops.html',
					{
					"proposed_workshops": proposed_workshops,
					"requested_workshops": requested_workshops,
					"scheduled_workshops": settings.SCHEDULED_WORKSHOPS
					})
	else:
		redirect('/book/')
