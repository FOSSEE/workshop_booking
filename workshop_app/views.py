try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io
from datetime import datetime

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import (
    UserRegistrationForm, UserLoginForm,
    ProfileForm, WorkshopForm
)
from .models import (
    Profile, User,
    Workshop,
    WorkshopType
)
from .send_mails import send_email

__author__ = "Akshen Doke"
__credits__ = ["Mahesh Gudi", "Aditya P.", "Ankit Javalkar",
               "Prathamesh Salunke", "Kiran Kishore",
               "KhushalSingh Rajput", "Prabhu Ramachandran",
               "Arun KP"]


# Helper functions

def is_email_checked(user):
    return user.profile.is_email_verified


def is_instructor(user):
    """Check if the user is having instructor rights"""
    return user.groups.filter(name='instructor').exists()


def get_landing_page(user):
    # For now, landing pages of both instructor and coordinator are same
    if is_instructor(user):
        return '/my_workshops/'
    return '/my_workshops/'


# View functions

def index(request):
    """Landing Page : Redirect to login page if not logged in
                      Redirect to respective landing page according to position"""
    user = request.user
    if user.is_authenticated and is_email_checked(user):
        return redirect(get_landing_page(user))

    return redirect('/login/')


# User views

# TODO: Forgot password workflow
def user_login(request):
    """User Login"""
    user = request.user
    if user.is_superuser:
        return redirect('/admin')
    if user.is_authenticated:
        return redirect(get_landing_page(user))

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            if user.profile.is_email_verified:
                login(request, user)
                return redirect(get_landing_page(user))
            else:
                return render(request, 'workshop_app/activation.html')
        else:
            return render(request, 'workshop_app/login.html', {"form": form})
    else:
        form = UserLoginForm()
        return render(request, 'workshop_app/login.html', {"form": form})


def user_logout(request):
    """Logout"""
    logout(request)
    return render(request, 'workshop_app/logout.html')


def activate_user(request, key=None):
    user = request.user
    if user.is_superuser:
        return redirect("/admin")
    if key is None:
        if user.is_authenticated and not user.profile.is_email_verified and \
                timezone.now() > user.profile.key_expiry_time:
            status = "1"
            Profile.objects.get(user_id=user.profile.user_id).delete()
            User.objects.get(id=user.profile.user_id).delete()
            return render(request, 'workshop_app/activation.html',
                          {'status': status})
        elif user.is_authenticated and not user.profile.is_email_verified:
            return render(request, 'workshop_app/activation.html')
        elif user.is_authenticated and user.profile.is_email_verified:
            status = "2"
            return render(request, 'workshop_app/activation.html',
                          {'status': status})
        else:
            return redirect('/register/')

    user = Profile.objects.filter(activation_key=key)
    if user.exists():
        user = user.first()
    else:
        logout(request)
        return redirect('/register/')

    user.is_email_verified = True
    user.save()
    status = "0"
    return render(request, 'workshop_app/activation.html',
                  {"status": status})


def user_register(request):
    """User Registration form"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
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
            if request.user.is_authenticated:
                return redirect('/view_profile/')
            return render(
                request, "workshop_app/registration/register.html",
                {"form": form}
            )
    else:
        if request.user.is_authenticated and is_email_checked(request.user):
            return redirect('/my_workshops/')
        elif request.user.is_authenticated:
            return render(request, 'workshop_app/activation.html')
        form = UserRegistrationForm()
    return render(request, "workshop_app/registration/register.html", {"form": form})


@login_required
def view_profile(request):
    """ view instructor and coordinator profile """
    user = request.user
    if user.is_superuser:
        return redirect('/admin')
    return render(request, "workshop_app/view_profile.html")


@login_required
def edit_profile(request):
    """ edit profile details facility for instructor and coordinator """

    user = request.user
    if user.is_superuser:
        return redirect('/admin')

    if request.method == 'POST':
        form = ProfileForm(request.POST, user=user, instance=user.profile)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = user
            form_data.user.first_name = request.POST['first_name']
            form_data.user.last_name = request.POST['last_name']
            form_data.user.save()
            form_data.save()

            return redirect('/view_profile/')
        else:
            return render(request, 'workshop_app/edit_profile.html')
    else:
        form = ProfileForm(user=user, instance=user.profile)
        return render(request, 'workshop_app/edit_profile.html', {'form': form})


# Workshop views

@login_required
def my_workshops(request):
    user = request.user

    if user.is_authenticated:
        # View for instructor
        if is_instructor(user):
            print('inst')
            if request.method == 'POST':
                client_data = request.POST
                action = request.POST.get('action')
                if action == 'accept':
                    workshop = Workshop.objects.get(id=client_data.get('workshop_id'))
                    # Change Status of the selected workshop
                    workshop.status = 1
                    workshop.instructor = user
                    workshop.save()
                    # Parameters for emails
                    coordinator_email = workshop.coordinator.email
                    coordinator_name = workshop.coordinator.profile.user.get_full_name()
                    coordinator_phone = workshop.coordinator.profile.phone_number
                    coordinator_institute = workshop.coordinator.profile.institute
                    instructor_phone = request.user.profile.phone_number
                    workshop_title = workshop.workshop_type.name
                    workshop_date = str(workshop.date)

                    # For Instructor
                    send_email(request, call_on='Booking Confirmed',
                               user_position='instructor',
                               workshop_date=workshop_date,
                               workshop_title=workshop_title,
                               user_name=str(coordinator_name),
                               other_email=coordinator_email,
                               phone_number=coordinator_phone,
                               institute=coordinator_institute
                               )

                    # For Coordinator
                    send_email(request, call_on='Booking Confirmed',
                               workshop_date=workshop_date,
                               workshop_title=workshop_title,
                               other_email=coordinator_email,
                               phone_number=instructor_phone
                               )

                elif action == 'change_date':
                    cid = client_data.get('cid')
                    new_workshop_date = datetime.strptime(client_data.get('new_date'), "%Y-%m-%d")
                    coordinator_email = User.objects.get(id=cid)
                    today = datetime.today()
                    if today > new_workshop_date:
                        # Invalid date
                        pass
                    else:
                        workshop = Workshop.objects.filter(id=client_data.get('workshop_id'))
                        workshop_date = workshop.first().date
                        workshop.update(date=new_workshop_date)

                        # For Instructor
                        send_email(request, call_on='Change Date',
                                   user_position='instructor',
                                   workshop_date=str(workshop_date),
                                   new_workshop_date=str(new_workshop_date.date())
                                   )

                        # For Coordinator
                        send_email(request, call_on='Change Date',
                                   new_workshop_date=str(new_workshop_date.date()),
                                   workshop_date=str(workshop_date),
                                   other_email=coordinator_email.email
                                   )

            today = timezone.now()
            proposed_workshop = Workshop.objects.filter(
                instructor=user.id,
                date__gte=today,
            ).order_by('-date')

            proposed_workshop_pending = Workshop.objects.filter(
                status=0
            ).order_by('-date')

            workshops = list(proposed_workshop) + list(proposed_workshop_pending)

            return render(request, 'workshop_app/my_workshops.html',
                          {"workshops": workshops,
                           "today": today})

        # Coordinator view
        else:
            workshops = Workshop.objects.filter(
                coordinator=user.id
            ).order_by('-date')
            return render(request, 'workshop_app/my_workshops.html',
                          {"workshops": workshops})
    # Not logged in view
    else:
        return redirect('/login/')


# TODO: Show terms n conditions of selected ws type
@login_required
def propose_workshop(request):
    """Coordinator proposed a workshop and date"""

    user = request.user
    if user.is_superuser:
        return redirect("/admin")
    if is_instructor(user):
        return redirect(get_landing_page(user))
    else:
        form = WorkshopForm()
        if request.method == 'POST':
            form = WorkshopForm(request.POST)
            if form.is_valid():
                form_data = form.save(commit=False)
                form_data.coordinator = user
                # Avoiding Duplicate workshop entries for same date and workshop_title
                if Workshop.objects.filter(
                        date=form_data.date,
                        workshop_type=form_data.workshop_type,
                        coordinator=form_data.coordinator
                ).exists():
                    return redirect('/my_workshops/')
                else:
                    form_data.save()
                    instructors = Profile.objects.filter(position='instructor')
                    for i in instructors:
                        send_email(request, call_on='Proposed Workshop',
                                   user_position='instructor',
                                   workshop_date=str(form_data.date),
                                   workshop_title=form_data.workshop_type,
                                   user_name=user.get_full_name(),
                                   other_email=i.user.email,
                                   phone_number=user.profile.phone_number,
                                   institute=user.profile.institute
                                   )
                    return redirect('/my_workshops/')
        # GET request
        print(form.errorlist_css_class)
        return render(
            request, 'workshop_app/propose_workshop.html',
            {"form": form}
        )


def workshop_type_details(request, workshop_type_id):
    """Gives the types of workshop details """
    user = request.user
    if user.is_superuser:
        return redirect("/admin")

    workshop_type = WorkshopType.objects.get(id=workshop_type_id)

    return render(
        request, 'workshop_app/workshop_type_details.html', {'workshop_type': workshop_type}
    )


def workshop_type_list(request):
    """Gives the details for types of workshops."""
    user = request.user
    if user.is_superuser:
        return redirect("/admin")

    workshop_types = WorkshopType.objects.all()

    paginator = Paginator(workshop_types, 12)  # Show upto 12 workshops per page

    page = request.GET.get('page')
    try:
        workshop_type = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        workshop_type = paginator.page(1)
    except EmptyPage:
        # If page is out of range(e.g 999999), deliver last page.
        workshop_type = paginator.get_page(paginator.num_pages)

    return render(request, 'workshop_app/workshop_type_list.html', {'workshop_type': workshop_type})


@login_required
def view_comment_profile(request, user_id):
    """instructor can view/post comments on coordinator profile """
    user = request.user
    if is_instructor(user) and is_email_checked(user):
        coordinator_profile = Profile.objects.get(user_id=user_id)
        workshops = Workshop.objects.filter(coordinator=user_id).order_by(
            'date')

        return render(request, "workshop_app/view_profile.html",
                      {"coordinator_profile": coordinator_profile,
                       "Workshops": workshops})
    return redirect(get_landing_page(user))
