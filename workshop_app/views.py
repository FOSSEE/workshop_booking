from .forms import (
					UserRegistrationForm, UserLoginForm, 
					ProfileForm, CreateWorkshop
					)
from .models import (
					Profile, User,
					has_profile, Workshop, 
					Course, RequestedWorkshop,
					BookedWorkshop
					)
from django.template import RequestContext
from datetime import datetime, date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db import IntegrityError
from collections import OrderedDict
from dateutil.parser import parse
from .send_mails import send_email
from django.http import HttpResponse


def index(request):
	'''Landing Page'''

	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/manage/')
		return redirect('/book/')

	return render(request, "workshop_app/index.html")


def is_instructor(user):
	'''Check if the user is having instructor rights'''
	if user.groups.filter(name='instructor').exists():
		return True


def user_login(request):
	'''Login'''
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


def user_register(request):
	'''User Registeration form'''
	if request.method == 'POST':
		form = UserRegistrationForm(request.POST)
		if form.is_valid():
			try:
				data = form.cleaned_data
				username, password = form.save()
				new_user = authenticate(username=username, password=password)
				login(request, new_user)
				user_position = request.user.profile.position
				send_email(
						   request, call_on='Registration', 
						   user_position=user_position
						  )
				return redirect('/view_profile/')
			except IntegrityError as e:
				return render(
							request, 
							"workshop_app/registeration_error.html"
							)
		else:
			return render(
						request, "workshop_app/register.html", 
						{"form": form}
						)
	else:
		form = UserRegistrationForm()
	return render(request, "workshop_app/register.html", {"form": form})


def book(request):
	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/manage/')

		workshop_details = Workshop.objects.all()
		workshop_occurence = {}
		for workshops in workshop_details:
			dates = workshops.recurrences.between(
				datetime(2017, 3, 12, 0, 0, 0),
	    		datetime(2017, 12, 31, 0, 0, 0), #Needs to be changed yearly
	    		inc=True
				)
			
			for d in range(len(dates)):
				workshop_occurence[dates[d].strftime("%d-%m-%Y")] = [
										workshops.workshop_instructor,
				 						workshops.workshop_title,
				 						workshops.workshop_instructor_id,
				 						workshops.workshop_title_id
				 						]
				
		# workshop_occurence = OrderedDict(sorted(workshop_occurence.items()))
		workshop_occurence = list(workshop_occurence.items())

		#Gives you the objects of BookedWorkshop
		requested_workshop = BookedWorkshop.objects.all()
		for j in requested_workshop:
			'''
			j.booked_workshop.requested_workshop_date returns object from 
			requestedworkshop table
			'''
			j = j.booked_workshop.requested_workshop_date.strftime("%d-%m-%Y")
			for i in workshop_occurence:
				if i[0] == j:
					workshop_occurence.remove(i)


		#Show upto 6 Workshops per page
		paginator = Paginator(workshop_occurence, 6) 
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
		return redirect('/login/')


@login_required
def book_workshop(request):
	'''
	Function for Updating requested_workshop table
	'''
	if request.method == 'POST':
		user_position = request.user.profile.position
		client_data = request.body.decode("utf-8").split("&")
		client_data = client_data[0].split("%2C")
		workshop_date = client_data[0][2:]

		instructor_profile = Profile.objects.filter(user=client_data[1])
		workshop = Workshop.objects.get(
										workshop_instructor=client_data[1]
										)
		workshop_recurrence_list =  workshop.recurrences.between(
									datetime(2017, 3, 12, 0, 0, 0),
									datetime(2017, 12, 31, 0, 0, 0),
									inc=True
									)

		rW_obj = RequestedWorkshop()

		workshop_obj = Workshop.objects.get(
								workshop_instructor=client_data[1], 
								workshop_title_id=client_data[2]
								)

		for d in workshop_recurrence_list:
			if workshop_date == (d.strftime("%d-%m-%Y")):
				# rW_obj = RequestedWorkshop()

				# workshop_obj = Workshop.objects.get(
				# 							workshop_instructor=client_data[1], 
				# 							workshop_title_id=client_data[2]
				# 							)
				rW_obj.requested_workshop_instructor = workshop_obj.workshop_instructor
				rW_obj.requested_workshop_coordinator = request.user
				rW_obj.requested_workshop_date = datetime.strptime(
														client_data[0][2:], "%d-%m-%Y"
														)
				rW_obj.requested_workshop_title = workshop_obj.workshop_title
				rW_obj.save()

		# Mail to instructor
		send_email(request, call_on='Booking', 
					   user_position='instructor', 
					   workshop_date=workshop_date,
					   workshop_title=workshop_obj.workshop_title.course_name,
					   user_name=str(request.user),
					   other_email=workshop_obj.workshop_instructor.email
					   )

		#Mail to coordinator
		send_email(request, call_on='Booking',
				workshop_date=workshop_date,
				workshop_title=workshop_obj.workshop_title.course_name,
				user_name=workshop_obj.workshop_instructor.username)
				
		return HttpResponse("Thank You, Please check your email for further \
							information.")
	else:
		return HttpResponse("Some Error Occurred.")


@login_required
def manage(request):
	user = request.user
	if user.is_authenticated():
		#Move user to the group via admin
		if user.groups.filter(name='instructor').count() > 0:
			try:
				#Can't Handle Multiple objects Fix this asap
				workshop_details = Workshop.objects.get(
													workshop_instructor=user.id
													)
				workshop_occurence_list = workshop_details.recurrences.between(
											datetime(2017, 3, 12, 0, 0, 0),
											datetime(2017, 12, 31, 0, 0, 0),
											inc=True													
											)

				for i in range(len(workshop_occurence_list)):
					workshop_occurence_list[i] = [{ 
									"user": str(user), 
									"workshop": workshop_details.workshop_title, 
									"date": workshop_occurence_list[i].date()
									}]


				requested_workshop = RequestedWorkshop.objects.filter(
										requested_workshop_instructor=user.id
										)
				
				#Need to recheck logic
				for j in range(len(requested_workshop)):
					for i in workshop_occurence_list:
						if i[0]['date'] == requested_workshop[j].requested_workshop_date:
							workshop_occurence_list.remove(i)


				#Show upto 3 Workshops per page
				paginator = Paginator(workshop_occurence_list, 3)
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
		return redirect('/login/')


@login_required
def my_workshops(request):
	user = request.user

	if user.is_authenticated():
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
										requested_workshop_coordinator=coordinator_obj.id
										)
					workshop_status.status = client_data[-1]
					workshop_status.save()
					confirm_workshop = BookedWorkshop()
					confirm_workshop.booked_workshop = workshop_status
					confirm_workshop.save()


					#For Instructor
					send_email(request, call_on='Booking Confirmed', 
						user_position='instructor', 
						workshop_date=str(client_data[1]),
						workshop_title=workshop_status.requested_workshop_title.course_name,
						user_name=str(request.user),
						)

					#For Coordinator
					send_email(request, call_on='Booking Confirmed',  
						workshop_date=str(client_data[1]),
						workshop_title=workshop_status.requested_workshop_title.course_name,
						other_email=workshop_status.requested_workshop_coordinator.email
						)

				elif client_data[-1] == 'DELETED':
					workshop_date = client_data[1]
					workshop = Workshop.objects.get(workshop_instructor=request.user.id,
														workshop_title_id=client_data[2])
					
					workshop_recurrence_list = workshop.recurrences.between(
												datetime(2017, 3, 12, 0, 0, 0),
												datetime(2017, 12, 31, 0, 0, 0),
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

					#For instructor
					send_email(request, call_on='Workshop Deleted',
						workshop_date=str(client_data[1]),
						)

					return HttpResponse("Workshop Deleted")
					
				else:
					#For Instructor
					send_email(request, call_on='Booking Request Rejected', 
						user_position='instructor', 
						workshop_date=str(client_data[1]),
						workshop_title=workshop_status.requested_workshop_title.course_name,
						user_name=str(request.user),
						)

					#For Coordinator
					send_email(request, call_on='Booking Request Rejected',
						workshop_date=str(client_data[1]),
						workshop_title=workshop_status.requested_workshop_title.course_name,
						other_email=workshop_status.requested_workshop_coordinator.email
						)

			workshop_occurence_list = RequestedWorkshop.objects.filter(
									requested_workshop_instructor=user.id
									)
			
			#Show upto 6 Workshops per page
			paginator = Paginator(workshop_occurence_list, 9)
			page = request.GET.get('page')
			try:
				workshop_occurences = paginator.page(page)
			except PageNotAnInteger:
			#If page is not an integer, deliver first page.
				workshop_occurences = paginator.page(1)
			except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
				workshop_occurences = paginator.page(paginator.num_pages)
			template = 'workshop_app/my_workshops.html'

			

		else:
			workshop_occurence_list = RequestedWorkshop.objects.filter(
									requested_workshop_coordinator=user.id
									)
			
			#Show upto 6 Workshops per page
			paginator = Paginator(workshop_occurence_list, 9)
			print(paginator) 
			page = request.GET.get('page')
			try:
				workshop_occurences = paginator.page(page)
			except PageNotAnInteger:
			#If page is not an integer, deliver first page.
				workshop_occurences = paginator.page(1)
			except EmptyPage:
				#If page is out of range(e.g 999999), deliver last page.
				workshop_occurences = paginator.page(paginator.num_pages)
			template = 'workshop_app/my_workshops.html'
	else:
		redirect('/login')

	return render(request, template,
				 {"workshop_occurences": workshop_occurences} 
				 )


@login_required
def view_profile(request):
	""" view instructor and coordinator profile """
	return render(request, "workshop_app/view_profile.html")


@login_required
def edit_profile(request):
	""" edit profile details facility for instructor and coordinator """

	user = request.user
	if is_instructor(user):
		template = 'workshop_app/manage.html'
	else:
		template = 'workshop_app/booking.html'
	context = {'template': template}
	if has_profile(user):
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
	if is_instructor(user):
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
def view_course_list(request):
	'''Gives the course details '''
	user = request.user
	if is_instructor(user):
		course_list = Course.objects.all()
		paginator = Paginator(course_list, 6) #Show upto 12 Courses per page

		page = request.GET.get('page')
		try:
			courses = paginator.page(page)
		except PageNotAnInteger:
			#If page is not an integer, deliver first page.
			courses = paginator.page(1)
		except EmptyPage:
			#If page is out of range(e.g 999999), deliver last page.
			courses = paginator.page(paginator.num_pages)

		return render(
					request, 'workshop_app/view_course_list.html', \
					{'courses': courses}
					)

	else:
		return redirect('/book/')


@login_required
def view_course_details(request):
	'''Gives the course details '''

	user = request.user
	if is_instructor(user):

		return redirect('/')
		
	else:
		return redirect('/book/')
