from django.conf.urls import url

from api import views

urlpatterns = [
    url(r'^upcoming_workshops$', views.UpcomingWorkshops.as_view(), name='index'),
]
