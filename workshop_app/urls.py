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
import django

js_info_dict = {
    'packages': ('recurrence', ),
}

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.user_register),
    url(r'^activate_user/(?P<key>.+)$', views.activate_user),
    url(r'^activate_user/$', views.activate_user),
    url(r'^login/$', views.user_login),
    url(r'^logout/$', views.user_logout),
    url(r'^view_profile/$', views.view_profile),
    url(r'^edit_profile/$', views.edit_profile),
    url(r'^book/$', views.book),
    url(r'^book_workshop/$', views.book_workshop),
    url(r'^my_workshops/$', views.my_workshops),
    url(r'^how_to_participate/$', views.how_to_participate),
    url(r'^faq/$', views.faq),
    url(r'^manage/$', views.manage),
    url(r'^view_workshoptype_list/$', views.view_workshoptype_list),
    url(r'^view_workshoptype_details/([1-9][0-9]*)$', \
        views.view_workshoptype_details),
    url(r'^create_workshop/$', views.create_workshop),
    url(r'^propose_workshop/$', views.propose_workshop),
    url(r'^workshop_stats/$', views.workshop_stats),
    url(r'^jsi18n/$', django.views.i18n.javascript_catalog, js_info_dict),
    url(r'^self_workshop', views.self_workshop),
 ]

