from django.shortcuts import render, redirect
from forms import UserRegistrationForm, UserLoginForm, ProfileForm
from .models import Profile, User, has_profile
from django.template import RequestContext
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
	'''Home'''
	return render(request, "home.html")

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
		return redirect('/view_profile/')

	if request.method == "POST":
		form = UserLoginForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data
			login(request, user)
			if user.groups.filter(name='instructor').count() > 0:
				return redirect('/manage/')
			return redirect('/view_profile/')
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
			data = form.cleaned_data
			username, password = form.save()
			new_user = authenticate(username=username, password=password)
			login(request, new_user)
			return redirect('/home')
		else:
			return render(request, "workshop_app/register.html", {"form": form})
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

def manage(request):
	user = request.user
	if user.is_authenticated():
		if user.groups.filter(name='instructor').count() > 0:
			return render(request, "workshop_app/manage.html")
		return redirect('/book/')
	else:
		return redirect('/login/')

@login_required
def view_profile(request):
	""" view moderators and users profile """
	return render(request, "workshop_app/view_profile.html")

@login_required
def edit_profile(request):
	""" edit profile details facility for instructor and students """

	user = request.user
	if is_instructor(user):
		template = 'workshop_app/manage.html'
	else:
		template = 'workshop_app/user.html'
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
			return my_render_to_response('workshop_app/edit_profile.html', context)
	else:
		form = ProfileForm(user=user, instance=profile)
		context['form'] = form
		return render(request, 'workshop_app/edit_profile.html', context)
