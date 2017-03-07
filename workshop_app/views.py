
from .forms import UserRegistrationForm, UserLoginForm, ProfileForm, CreateWorkshop
from .models import Profile, User, has_profile, Workshop, Course
from django.template import RequestContext
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.db import IntegrityError


def index(request):
	'''Landing Page'''
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
				send_email(request, call_on='Registration', 
						   user_position=user_position)
				return redirect('/view_profile/')
			except IntegrityError as e:
				return render(request, 
						"workshop_app/registeration_error.html")
		else:
			return render(request, "workshop_app/register.html", 
						{"form": form})
	else:
		form = UserRegistrationForm()
	return render(request, "workshop_app/register.html", {"form": form})


def book(request):
	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return redirect('/manage/')
		return render(request, "workshop_app/booking.html")
	else:
		return redirect('/login/')

@login_required
def manage(request):
	user = request.user
	if user.is_authenticated():
		print user.id, user
		if user.groups.filter(name='instructor').count() > 0: #Move user to the group via admin 
			workshop_details = Workshop.objects.all()
			return render(request, "workshop_app/manage.html", {"workshop_details": workshop_details})
		return redirect('/book/')
	else:
		return redirect('/login/')

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

			return render(request, 'workshop_app/profile_updated.html', context)
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
				form.save()
				return redirect('/manage/')
		else:
			form = CreateWorkshop()
		return render(request, 'workshop_app/create_workshop.html', {"form": form })
	else:
		return redirect('/book/')

@login_required
def view_course_list(request):
	'''Gives the course details '''
	user = request.user
	if is_instructor(user):
		course_list = Course.objects.all()
		paginator = Paginator(course_list, 9) #Show upto 12 Courses per page

		page = request.GET.get('page')
		try:
			courses = paginator.page(page)
		except PageNotAnInteger:
			#If page is not an integer, deliver first page.
			courses = paginator.page(1)
		except EmptyPage:
			#If page is out of range(e.g 999999), deliver last page.
			courses = paginator.page(paginator.num_pages)

		return render(request, 'workshop_app/view_course_list.html', \
			{'courses': courses})

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

def send_email(request, call_on, user_position=None):
	'''
	Email sending function
	'''

	if call_on == 'Registration':
		if user_position == 'instructor':
			pass
		else:
			pass

	elif call_on == 'Booking':
		pass

