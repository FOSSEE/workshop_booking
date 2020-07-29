from django.conf.urls import url

from cms import views

app_name = "cms"

urlpatterns = [
    url('^$', views.home, name='home'),
    url('^(?P<permalink>.+)$', views.home, name='home')
]