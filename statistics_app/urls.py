
from django.conf.urls import url
from django.contrib import admin
from statistics_app import views


urlpatterns = [
	 url(r'^statistics/$', views.workshop_stats),
	 url(r'^statistics/public_stats/$', views.workshop_public_stats),
	 url(r'^statistics/profile_stats/$', views.profile_stats),
	 url(r'^statistics/v1/team_stats/$', views.team_stats),
]
