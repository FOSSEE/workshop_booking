from workshop_app.forms import (
    UserRegistrationForm, UserLoginForm,
    ProfileForm, CreateWorkshop,
    ProposeWorkshopDateForm
)
from workshop_app.models import (
    Profile, User,
    has_profile, Workshop,
    WorkshopType, RequestedWorkshop,
    BookedWorkshop, ProposeWorkshopDate,
    Testimonial
)
from django.template.loader import get_template
from django.template import RequestContext
from datetime import datetime, date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from os import listdir, path, sep
from zipfile import ZipFile
from django.contrib import messages
from operator import itemgetter
import datetime as dt
import csv
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io


# Create your views here.
def check_workshop_type(x):
    try:
        y = datetime.strftime(x.proposed_workshop_date, '%d-%m-%Y')
    except BaseException:
        y = datetime.strftime(x.requested_workshop_date, '%d-%m-%Y')
    return y


def is_instructor(user):
    '''Check if the user is having instructor rights'''
    return True if user.groups.filter(name='instructor').count() > 0 else False


def is_email_checked(user):
    if hasattr(user, 'profile'):
        return True if user.profile.is_email_verified else False
    else:
        return False


def pie_chart():
    '''This function gives Data for drawring Pie Chart'''

    # Count Total Number of workshops for each type
    workshop_titles = WorkshopType.objects.all()
    workshoptype_dict = {}
    for title in workshop_titles:
        workshoptype_dict[title] = 0

    for title in workshoptype_dict.keys():
        workshoptype_dict[title] += RequestedWorkshop.objects.filter(
            requested_workshop_title=title,
            status='ACCEPTED').count()
        workshoptype_dict[title] += ProposeWorkshopDate.objects.filter(
            proposed_workshop_title=title,
            status='ACCEPTED').count()

    # For Pie Chart
    workshoptype_num = [count for count in workshoptype_dict.values()]
    workshoptype_title = [str(title) for title in workshoptype_dict.keys()]

    workshoptype_count = [workshoptype_title, workshoptype_num]
    del workshoptype_title, workshoptype_num

    return workshoptype_count


def india_map():
   '''This function returns count of workshops based on states in India.''' 

   states = [
        ['Code', 'State', 'Number'],
        ["IN-AP", "Andhra Pradesh", 0],
        ["IN-AR", "Arunachal Pradesh", 0],
        ["IN-AS", "Assam", 0],
        ["IN-BR", "Bihar", 0],
        ["IN-CT", "Chhattisgarh", 0],
        ["IN-GA", "Goa", 0],
        ["IN-GJ", "Gujarat", 0],
        ["IN-HR", "Haryana", 0],
        ["IN-HP", "Himachal Pradesh", 0],
        ["IN-JK", "Jammu and Kashmir", 0],
        ["IN-JH", "Jharkhand", 0],
        ["IN-KA", "Karnataka", 0],
        ["IN-KL", "Kerala", 0],
        ["IN-MP", "Madhya Pradesh", 0],
        ["IN-MH", "Maharashtra", 0],
        ["IN-MN", "Manipur", 0],
        ["IN-ML", "Meghalaya", 0],
        ["IN-MZ", "Mizoram", 0],
        ["IN-NL", "Nagaland", 0],
        ["IN-OR", "Odisha", 0],
        ["IN-PB", "Punjab", 0],
        ["IN-RJ", "Rajasthan", 0],
        ["IN-SK", "Sikkim", 0],
        ["IN-TN", "Tamil Nadu", 0],
        ["IN-TG", "Telangana", 0],
        ["IN-TR", "Tripura", 0],
        ["IN-UT", "Uttarakhand", 0],
        ["IN-UP", "Uttar Pradesh", 0],
        ["IN-WB", "West Bengal", 0],
        ["IN-AN", "Andaman and Nicobar Islands", 0],
        ["IN-CH", "Chandigarh", 0],
        ["IN-DN", "Dadra and Nagar Haveli", 0],
        ["IN-DD", "Daman and Diu", 0],
        ["IN-DL", "Delhi", 0],
        ["IN-LD", "Lakshadweep", 0],
        ["IN-PY", "Puducherry", 0]
    ]
   workshop_state = []
   requestedWorkshops = RequestedWorkshop.objects.filter(status='ACCEPTED')
   proposedWorkshops = ProposeWorkshopDate.objects.filter(status='ACCEPTED')
   for workshop in requestedWorkshops:
       for s in states:
           if s[0] == workshop.requested_workshop_coordinator.profile.state:
               s[2] += 1

   for workshop in proposedWorkshops:
       for s in states:
           if s[0] == workshop.proposed_workshop_coordinator.profile.state:
               s[2] += 1

   return states



@login_required
def workshop_stats(request):
    user = request.user
    today = datetime.now()
    upto = today + dt.timedelta(days=15)

    # For Monthly Chart
    workshop_count = [0] * 12
    for x in range(12):
        workshop_count[x] += RequestedWorkshop.objects.filter(
            requested_workshop_date__year=str(today.year),
            requested_workshop_date__month=str(x + 1),
            status='ACCEPTED').count()
        workshop_count[x] += ProposeWorkshopDate.objects.filter(
            proposed_workshop_date__year=str(today.year),
            proposed_workshop_date__month=str(x + 1),
            status='ACCEPTED').count()

    # For Pie Chart
    workshoptype_count = pie_chart()

    # For India Map
    states = india_map()
    # For Data Downloading and Viewing
    if request.method == 'POST':
        try:
            from_dates = request.POST.get('from')
            to_dates = request.POST.get('to')

            # Fetches Accepted workshops which were proposed by Coordinators
            proposed_workshops = ProposeWorkshopDate.objects.filter(
                proposed_workshop_date__range=(from_dates, to_dates),
                status='ACCEPTED'
            )

            # Fetches Accepted workshops which were Accepted by
            # Instructors based on their Availability
            requested_workshops = RequestedWorkshop.objects.filter(
                requested_workshop_date__range=(from_dates, to_dates),
                status='ACCEPTED'
            )

            upcoming_workshops = []

            for workshop in proposed_workshops:
                upcoming_workshops.append(workshop)

            for workshop in requested_workshops:
                upcoming_workshops.append(workshop)

            upcoming_workshops = sorted(upcoming_workshops,
                                        key=lambda x: check_workshop_type(x))

            download = request.POST.get('Download')
            if download:
                response = HttpResponse(content_type='text/csv')

                response['Content-Disposition'] = 'attachment;\
                                filename="records_from_{0}_to_{1}.csv"'.format(
                    from_dates, to_dates
                )

                writer = csv.writer(response)
                header = [
                    'coordinator name',
                    'coordinator email',
                    'instructor name',
                    'workshop',
                    'date',
                    'status',
                    'institute name',
                    'state'
                ]

                writer.writerow(header)

                for workshop in upcoming_workshops:
                    try:
                        row = [
                       workshop.proposed_workshop_coordinator,
                       str(workshop.propossed_workshop_coordinator.profile.user.email),
                       workshop.proposed_workshop_instructor,
                       workshop.proposed_workshop_title,
                       workshop.proposed_workshop_date,
                       workshop.status,
                       workshop.proposed_workshop_coordinator.profile.institute,
                       str(workshop.proposed_workshop_coordinator.profile.state)
                        ]

                    except BaseException:
                        row = [
                        workshop.requested_workshop_coordinator,
                        str(workshop.requested_workshop_coordinator.profile.user.email),
                        workshop.requested_workshop_instructor,
                        workshop.requested_workshop_title,
                        workshop.requested_workshop_date,
                        workshop.status,
                        workshop.requested_workshop_coordinator.profile.institute,
                        str(workshop.requested_workshop_coordinator.profile.state)
                        ]

                    writer.writerow(row)
                return response
            else:
                return render(request,
                              'statistics_app/workshop_stats.html',
                              {"upcoming_workshops": upcoming_workshops,
                               "show_workshop_stats": settings.SHOW_WORKSHOP_STATS,
                               "workshop_count": workshop_count,
                               "workshoptype_count": workshoptype_count,
                               "india_map": states})
        except BaseException:
            messages.info(request, 'Please enter Valid Dates')

    if is_instructor(user) and is_email_checked(user):
        try:
            # Fetches Accepted workshops which were proposed by Coordinators
            proposed_workshops = ProposeWorkshopDate.objects.filter(
                proposed_workshop_date__range=(today, upto),
                status='ACCEPTED'
            )

            # Fetches Accepted workshops which were Accepted by
            # Instructors based on their Availability
            requested_workshops = RequestedWorkshop.objects.filter(
                requested_workshop_date__range=(today, upto),
                status='ACCEPTED'
            )

            upcoming_workshops = []
            for workshop in proposed_workshops:
                upcoming_workshops.append(workshop)

            for workshop in requested_workshops:
                upcoming_workshops.append(workshop)

            upcoming_workshops = sorted(upcoming_workshops,
                                        key=lambda x: check_workshop_type(x))

        except BaseException:
            upcoming_workshops = []

        paginator = Paginator(upcoming_workshops, 12)

        page = request.GET.get('page')
        try:
            upcoming_workshops = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            upcoming_workshops = paginator.page(1)
        except EmptyPage:
            # If page is out of range(e.g 999999), deliver last page.
            upcoming_workshops = paginator.page(paginator.num_pages)

        return render(request, 'statistics_app/workshop_stats.html',
                      {
                          "upcoming_workshops": upcoming_workshops,
                          "show_workshop_stats": settings.SHOW_WORKSHOP_STATS,
                          "workshop_count": workshop_count,
                          "workshoptype_count": workshoptype_count,
                          "india_map": states
                      })
    else:
       return redirect('/statistics/public_stats/')


def workshop_public_stats(request):
    user = request.user
    today = datetime.now()
    upto = today + dt.timedelta(days=15)

    #For Pie Chart
    workshoptype_count = pie_chart()

    # For India Map
    states = india_map()

    # Select By WorkshopType
    workshoptype_list = list(WorkshopType.objects.all())
    workshoptype_list.append('all')

    # For Data Viewing
    if request.method == 'POST':
        workshop_list = []

        try:
            from_dates = request.POST.get('from')
            to_dates = request.POST.get('to')
            selected_state = request.POST.get('states')
            selected_workshoptype = request.POST.get('workshoptype_name')
            if selected_state == 'all':
                # If dates not passed
                if len(from_dates) == 0 and len(to_dates) == 0:
                    from_dates = '2017-01-01'
                    to_dates = upto
                # If SelectedWorkshopType is 'All'
                if len(selected_workshoptype) == 0:
                    # Fetches Accepted workshops which were proposed by
                    # Coordinators
                    proposed_workshops = ProposeWorkshopDate.objects.filter(
                        proposed_workshop_date__range=(from_dates, to_dates),
                        status='ACCEPTED'
                    )

                    # Fetches Accepted workshops which were Accepted by
                    # Instructors based on their Availability
                    requested_workshops = RequestedWorkshop.objects.filter(
                        requested_workshop_date__range=(from_dates, to_dates),
                        status='ACCEPTED'
                    )

                else:
                    # Fetches Accepted workshops which were proposed by
                    # Coordinators
                    proposed_workshops = ProposeWorkshopDate.objects.filter(
                        proposed_workshop_date__range=(from_dates, to_dates),
                        status='ACCEPTED', proposed_workshop_title_id=int(selected_workshoptype)
                    )

                    # Fetches Accepted workshops which were Accepted by
                    # Instructors based on their Availability
                    requested_workshops = RequestedWorkshop.objects.filter(
                        requested_workshop_date__range=(from_dates, to_dates),
                        status='ACCEPTED', requested_workshop_title_id=int(selected_workshoptype)
                    )

                for workshop in proposed_workshops:
                    workshop_list.append(workshop)

                for workshop in requested_workshops:
                    workshop_list.append(workshop)

            else:
                # If dates not passed
                if len(from_dates) == 0 and len(to_dates) == 0:
                    from_dates = '2017-01-01'
                    to_dates = upto

                # Get list of coordinators
                coordinators_state_wise = Profile.objects.filter(
                    state=selected_state)

                if len(selected_workshoptype) == 0:
                    # Traverse through list of coordinators and append
                    # workshop_list
                    for coordinator in coordinators_state_wise:
                        # Fetches Accepted workshops which were proposed by
                        # Coordinators
                        proposed_workshops = ProposeWorkshopDate.objects.filter(
                            proposed_workshop_date__range=(
                                from_dates,
                                to_dates),
                            status='ACCEPTED',
                            proposed_workshop_coordinator=coordinator.user_id)

                        # Fetches Accepted workshops which were Accepted by
                        # Instructors based on their Availability
                        requested_workshops = RequestedWorkshop.objects.filter(
                            requested_workshop_date__range=(
                                from_dates,
                                to_dates),
                            status='ACCEPTED',
                            requested_workshop_coordinator=coordinator.user_id)

                        for workshop in proposed_workshops:
                            workshop_list.append(workshop)

                        for workshop in requested_workshops:
                            workshop_list.append(workshop)

                else:
                   # Traverse through list of coordinators and append
                    # workshop_list
                    for coordinator in coordinators_state_wise:
                        # Fetches Accepted workshops which were proposed by
                        # Coordinators
                        proposed_workshops = ProposeWorkshopDate.objects.filter(
                            proposed_workshop_date__range=(
                                from_dates,
                                to_dates),
                            status='ACCEPTED', proposed_workshop_title_id=int(selected_workshoptype),
                            proposed_workshop_coordinator=coordinator.user_id)

                        # Fetches Accepted workshops which were Accepted by
                        # Instructors based on their Availability
                        requested_workshops = RequestedWorkshop.objects.filter(
                            requested_workshop_date__range=(
                                from_dates,
                                to_dates),
                            status='ACCEPTED', requested_workshop_title_id=int(selected_workshoptype),
                            requested_workshop_coordinator=coordinator.user_id)

                        for workshop in proposed_workshops:
                            workshop_list.append(workshop)

                        for workshop in requested_workshops:
                            workshop_list.append(workshop)

            return render(request,
                          'statistics_app/workshop_public_stats.html',
                          {
                              "workshoptype_list": workshoptype_list[::-1],
                              "workshop_list": workshop_list,
                              "workshoptype_count": workshoptype_count,
                              "india_map": states})

        except BaseException:
            messages.info(request, 'Please enter Valid Dates')

    else:
        '''Default Data'''
        workshop_list = []
        
        proposed_workshops = ProposeWorkshopDate.objects.filter(
                        status='ACCEPTED')

        # Fetches Accepted workshops which were Accepted by
        # Instructors based on their Availability
        requested_workshops = RequestedWorkshop.objects.filter(    
                    status='ACCEPTED')

        for workshop in proposed_workshops:
            workshop_list.append(workshop)

        for workshop in requested_workshops:
            workshop_list.append(workshop)


    return render(request,
                  'statistics_app/workshop_public_stats.html',
                  {
                      "workshoptype_list": workshoptype_list[::-1],
                      "workshoptype_count": workshoptype_count,
                      "workshop_list": workshop_list,
                      "india_map": states})


@login_required
def profile_stats(request):
    user = request.user
    if is_instructor(user) and is_email_checked(user):
        profiles = Profile.objects.all()

        rworkshops = RequestedWorkshop.objects.filter(status='ACCEPTED')
        pworkshops = ProposeWorkshopDate.objects.filter(status='ACCEPTED')

        iprofile = Profile.objects.filter(position='instructor')
        cprofile = Profile.objects.filter(position='coordinator')

        instructor_profile = []
        coordinator_profile = []

        for p in iprofile:
            instructor_profile.append({"profile": p,
                                        "count": 0
                                        })
            

        for p in cprofile:
            coordinator_profile.append({"profile": p,
                                        "count": 0
                                        })

        for p in instructor_profile:
            p['count'] += RequestedWorkshop.objects.filter(
                        requested_workshop_instructor_id=p['profile'].user.id,
                        status='ACCEPTED').count()

            p['count'] += ProposeWorkshopDate.objects.filter(
                        proposed_workshop_instructor_id=p['profile'].user.id,
                        status='ACCEPTED').count()

        for p in coordinator_profile:
            p['count'] += RequestedWorkshop.objects.filter(
                        requested_workshop_coordinator_id=p['profile'].user.id,
                        status='ACCEPTED').count()

            p['count'] += ProposeWorkshopDate.objects.filter(
                        proposed_workshop_coordinator_id=p['profile'].user.id,
                        status='ACCEPTED').count()

        #Sorting
        coordinator_profile = sorted(coordinator_profile, 
                            key=lambda k:k['count'], reverse=True)
        instructor_profile = sorted(instructor_profile, 
                            key=lambda k:k['count'], reverse=True)

        return render(request, "statistics_app/profile_stats.html",
            {
                "instructor_data": instructor_profile,
                "coordinator_data": coordinator_profile,
            })
    else:
        logout(request)
        return render(request, "workshop_app/logout.html")
