# Create your views here.
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import render

from cms.models import Page, Nav, SubNav


def home(request, permalink=''):
    if permalink == '':
        permalink = 'home'
    page = Page.objects.filter(permalink=permalink)
    nav_objs = Nav.objects.all().order_by('-position')
    subnav_objects = SubNav.objects.all()

    navs = []

    for nav in nav_objs:
        nav_obj = model_to_dict(nav)
        nav_obj['subnavs'] = subnav_objects.filter(nav=nav).order_by('position')
        navs.insert(-1, nav_obj)

    print(navs)

    if page.exists():
        page = page.first()
    else:
        raise Http404()

    return render(request, 'cms_base.html', {'page': page, 'navs': navs})
