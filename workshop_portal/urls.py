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
import django 

js_info_dict = {
    'packages': ('recurrence', ),
}


urlpatterns = [
    url(r'^workshop_booking/$', views.index, name='index'),
    url(r'^workshop_booking/admin/', admin.site.urls),
    url(r'^workshop_booking/register/$', views.user_register),
    url(r'^workshop_booking/activate_user/(?P<key>.+)$', views.activate_user),
    url(r'^workshop_booking/login/$', views.user_login),
    url(r'^workshop_booking/logout/$', views.user_logout),
    url(r'^workshop_booking/view_profile/$', views.view_profile),
    url(r'^workshop_booking/edit_profile/$', views.edit_profile),
    url(r'^workshop_booking/book/$', views.book),
    url(r'^workshop_booking/book_workshop/$', views.book_workshop),
    url(r'^workshop_booking/my_workshops/$', views.my_workshops),
    url(r'^workshop_booking/benefits/$', views.benefits),
    url(r'^workshop_booking/how_to_participate/$', views.how_to_participate),
    url(r'^workshop_booking/faq/$', views.faq),
    url(r'^workshop_booking/manage/$', views.manage),
    url(r'^workshop_booking/view_workshoptype_list/$', views.view_workshoptype_list),
    url(r'^workshop_booking/view_workshoptype_details/$', views.view_workshoptype_details),
    url(r'^workshop_booking/create_workshop/$', views.create_workshop),
    url(r'^workshop_booking/propose_workshop/$', views.propose_workshop),
    url(r'^workshop_booking/jsi18n/$', django.views.i18n.javascript_catalog, js_info_dict),

]
