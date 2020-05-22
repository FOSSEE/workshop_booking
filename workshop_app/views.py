from django.db.models import Q
from django.forms import inlineformset_factory, model_to_dict
from django.http import JsonResponse, Http404
from django.urls import reverse

try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io
from datetime import datetime

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import (
    UserRegistrationForm, UserLoginForm,
    ProfileForm, WorkshopForm, CommentsForm, WorkshopTypeForm
)
from .models import (
    Profile, User,
    Workshop, Comment,
    WorkshopType, AttachmentFile
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


def instructor_only(func):
    def inner1(*args, **kwargs):
        if is_instructor(args[0].user):
            return func(*args, **kwargs)
        return redirect(reverse('workshop_status_coordinator'))

    return inner1


def coordinator_only(func):
    def inner1(*args, **kwargs):
        if not is_instructor(args[0].user):
            return func(*args, **kwargs)
        return redirect(reverse('workshop_status_instructor'))

    return inner1


def redirect_to_landing_page(user):
    if is_instructor(user):
        return reverse('workshop_status_instructor')
    return reverse('workshop_status_coordinator')


# View functions

@login_required()
@instructor_only
@coordinator_only
def index(request):
    """Landing Page : Redirect to login page if not logged in
                      Redirect to respective landing page according to position"""
    pass


# User views

# TODO: Forgot password workflow
def user_login(request):
    """User Login"""
    user = request.user
    if user.is_superuser:
        return redirect('/admin')
    if user.is_authenticated:
        return redirect_to_landing_page(user)

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            if user.profile.is_email_verified:
                login(request, user)
                return redirect_to_landing_page(user)
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
            return redirect_to_landing_page(request.user)
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
@coordinator_only
def workshop_status_coordinator(request):
    """ Workshops proposed by Coordinator """
    user = request.user
    workshops = Workshop.objects.filter(
        coordinator=user.id
    ).order_by('-date')
    return render(request, 'workshop_app/workshop_status_coordinator.html',
                  {"workshops": workshops})


@login_required
@instructor_only
def workshop_status_instructor(request):
    """ Workshops to accept and accepted by Instructor """
    user = request.user
    today = timezone.now().date()
    workshops = Workshop.objects.filter(Q(
        instructor=user.id,
        date__gte=today,
    ) | Q(status=0)).order_by('-date')

    return render(request, 'workshop_app/workshop_status_instructor.html',
                  {"workshops": workshops,
                   "today": today})


@login_required
@instructor_only
def accept_workshop(request, workshop_id):
    user = request.user
    workshop = Workshop.objects.get(id=workshop_id)
    # Change Status of the selected workshop
    workshop.status = 1
    workshop.instructor = user
    workshop.save()

    coordinator_profile = workshop.coordinator.profile

    # For Instructor
    send_email(request, call_on='Booking Confirmed',
               user_position='instructor',
               workshop_date=str(workshop.date),
               workshop_title=workshop.workshop_type.name,
               user_name=str(coordinator_profile.user.get_full_name()),
               other_email=workshop.coordinator.email,
               phone_number=coordinator_profile.phone_number,
               institute=coordinator_profile.institute
               )

    # For Coordinator
    send_email(request, call_on='Booking Confirmed',
               workshop_date=str(workshop.date),
               workshop_title=workshop.workshop_type.name,
               other_email=workshop.coordinator.email,
               phone_number=request.user.profile.phone_number
               )
    return redirect(reverse('workshop_status_instructor'))


@login_required
@instructor_only
def change_workshop_date(request, workshop_id):
    if request.method == 'POST':
        new_workshop_date = datetime.strptime(request.POST.get('new_date'), "%Y-%m-%d")
        today = datetime.today()
        if today <= new_workshop_date:
            workshop = Workshop.objects.filter(id=workshop_id)
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
                       other_email=workshop.first().coordinator.email
                       )
    return redirect(reverse('workshop_status_instructor'))


# TODO: Show terms n conditions of selected ws type
@login_required
@coordinator_only
def propose_workshop(request):
    """Coordinator proposed a workshop and date"""

    user = request.user
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
                return redirect(reverse('workshop_status_coordinator'))
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
                return redirect(reverse('workshop_status_coordinator'))
    # GET request
    return render(
        request, 'workshop_app/propose_workshop.html',
        {"form": form}
    )


@login_required
def workshop_type_details(request, workshop_type_id):
    """Gives the types of workshop details """
    user = request.user
    if user.is_superuser:
        return redirect("/admin")

    workshop_type = WorkshopType.objects.filter(id=workshop_type_id)
    if workshop_type.exists():
        workshop_type = workshop_type.first()
    else:
        return redirect(reverse('workshop_type_list'))

    qs = AttachmentFile.objects.filter(workshop_type=workshop_type)
    AttachmentFileFormSet = inlineformset_factory(WorkshopType, AttachmentFile, fields=['attachments'],
                                                  can_delete=False, extra=(qs.count() + 1))

    if is_instructor(user):
        if request.method == 'POST':
            form = WorkshopTypeForm(request.POST, instance=workshop_type)
            form_file = AttachmentFileFormSet(request.POST, request.FILES, instance=form.instance)
            if form.is_valid():
                form_data = form.save()
                for file in form_file:
                    if file.is_valid() and file.clean() and file.clean()['attachments']:
                        if file.cleaned_data['id']:
                            file.cleaned_data['id'].delete()
                        file.save()
                return redirect(reverse('workshop_type_details', args=[form_data.id]))
        else:
            form = WorkshopTypeForm(instance=workshop_type)
        form_file = AttachmentFileFormSet()
        for subform, data in zip(form_file, qs):
            subform.initial = model_to_dict(data)
        return render(request, 'workshop_app/edit_workshop_type.html', {'form': form, 'form_file': form_file})

    return render(
        request, 'workshop_app/workshop_type_details.html', {'workshop_type': workshop_type}
    )


@login_required
@instructor_only
def delete_attachment_file(request, file_id):
    file = AttachmentFile.objects.filter(id=file_id)
    if file.exists():
        file = file.first()
        file.delete()
        return redirect(reverse('workshop_type_details', args=[file.workshop_type.id]))
    return redirect(reverse('workshop_type_list'))


@login_required
def workshop_type_tnc(request, workshop_type_id):
    workshop_type = WorkshopType.objects.filter(id=workshop_type_id)
    if workshop_type.exists():
        workshop_type = workshop_type.first()
        return JsonResponse({'tnc': workshop_type.terms_and_conditions})
    else:
        raise Http404


def workshop_type_list(request):
    """Gives the details for types of workshops."""
    user = request.user
    if user.is_superuser:
        return redirect("/admin")

    workshop_types = WorkshopType.objects.all()

    paginator = Paginator(workshop_types, 12)  # Show upto 12 workshops per page
    page = request.GET.get('page')
    workshop_type = paginator.get_page(page)

    return render(request, 'workshop_app/workshop_type_list.html', {'workshop_type': workshop_type})


@login_required
def workshop_details(request, workshop_id):
    workshop = Workshop.objects.filter(id=workshop_id)
    if not workshop.exists():
        raise Http404
    workshop = workshop.first()
    if request.method == 'POST':
        form = CommentsForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            if not is_instructor(request.user):
                form_data.public = True
            form_data.author = request.user
            form_data.created_date = timezone.now()
            form_data.workshop = workshop
            form.save()
        else:
            print(form.errors)
    if is_instructor(request.user):
        workshop_comments = Comment.objects.filter(workshop=workshop)
    else:
        workshop_comments = Comment.objects.filter(workshop=workshop, public=True)
    return render(request, 'workshop_app/workshop_details.html',
                  {'workshop': workshop, 'workshop_comments': workshop_comments,
                   'form': CommentsForm(initial={'public': True})})


@login_required
@instructor_only
def add_workshop_type(request):
    if request.method == 'POST':
        form = WorkshopTypeForm(request.POST)
        if form.is_valid():
            form_data = form.save()
            return redirect(reverse('workshop_type_details', args=[form_data.id]))
    else:
        form = WorkshopTypeForm
    return render(request, 'workshop_app/add_workshop_type.html', {'form': form})


@login_required
@instructor_only
def view_comment_profile(request, user_id):
    """Instructor can view coordinator profile """
    coordinator_profile = Profile.objects.get(user_id=user_id)
    workshops = Workshop.objects.filter(coordinator=user_id).order_by(
        'date')

    return render(request, "workshop_app/view_profile.html",
                  {"coordinator_profile": coordinator_profile,
                   "Workshops": workshops})
