
from django.conf.urls import url
from django.contrib import admin
from statistics_app import views
import django



urlpatterns = [
	 url(r'^statistics/$', views.workshop_stats),
	 url(r'^statistics/public_stats/$', views.workshop_public_stats),
]
