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
from django.contrib import admin
from workshop_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.user_login),
    url(r'^logout/$', views.user_logout),
    url(r'^register/$', views.user_register),
    url(r'^book/$', views.book),
    url(r'^manage/$', views.manage),
    url(r'^view_profile/$', views.view_profile),
    url(r'^edit_profile/$', views.edit_profile)
]
