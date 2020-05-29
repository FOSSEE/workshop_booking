from django.shortcuts import redirect
from django.urls import reverse


def instructor_only(func):
    def inner(*args, **kwargs):
        if is_instructor(args[0].user):
            return func(*args, **kwargs)
        return redirect(reverse('workshop_status_coordinator'))

    return inner


def coordinator_only(func):
    def inner(*args, **kwargs):
        if not is_instructor(args[0].user):
            return func(*args, **kwargs)
        return redirect(reverse('workshop_status_instructor'))

    return inner


def is_instructor(user):
    """Check if the user is having instructor rights"""
    return user.groups.filter(name='instructor').exists()
