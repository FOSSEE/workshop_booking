"""workshop_portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from workshop_app import views

urlpatterns = [
    url(r'^register/$', views.user_register),
    url(r'^activate_user/(?P<key>.+)$', views.activate_user),
    url(r'^activate_user/$', views.activate_user),
    url(r'^login/$', views.user_login),
    url(r'^logout/$', views.user_logout),
    url(r'^view_profile/$', views.view_profile),
    url(r'^edit_profile/$', views.edit_profile),
    url(r'^workshop_status$', views.workshop_status_coordinator, name='workshop_status_coordinator'),
    url(r'^dashboard$', views.workshop_status_instructor, name='workshop_status_instructor'),
    url(r'^accept_workshop/(?P<workshop_id>\d+)', views.accept_workshop, name='accept_workshop'),
    url(r'^change_workshop_date/(?P<workshop_id>\d+)$', views.change_workshop_date, name='change_workshop_date'),
    url(r'^propose_workshop/$', views.propose_workshop, name='propose_workshop'),
    url(r'^add_workshop_type$', views.add_workshop_type, name='add_workshop_type'),
    url(r'^delete_attachment_file/(?P<file_id>\d+)$', views.delete_attachment_file, name='delete_attachment_file'),
    url(r'^workshop_types/$', views.workshop_type_list, name='workshop_type_list'),
    url(r'^workshop_type_details/(?P<workshop_type_id>\d+)$', views.workshop_type_details, name='workshop_type_details'),
    url(r'^view_profile/(?P<user_id>\d+)$', views.view_comment_profile, name='view_profile'),
    url(r'^workshop_type_tnc/(?P<workshop_type_id>\d+)$', views.workshop_type_tnc, name='workshop_type_tnc'),
]
