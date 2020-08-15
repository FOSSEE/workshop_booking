from string import punctuation, digits

from django import forms
from django.utils import timezone

from .models import (Profile, Workshop, Comment, department_choices, title, source, states, WorkshopType,
                     AttachmentFile)

try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .send_mails import generate_activation_key

UNAME_CHARS = letters + "._" + digits
PWD_CHARS = letters + punctuation + digits


class UserRegistrationForm(forms.Form):
    """A Class to create new form for User's Registration.
    It has the various fields and functions required to register
    a new user to the system"""
    required_css_class = 'required'
    errorlist_css_class = 'errorlist'
    username = forms.CharField(max_length=32, help_text='''Letters, digits,
                               period and underscore only.''')
    email = forms.EmailField()
    password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=32, widget=forms.PasswordInput())
    title = forms.ChoiceField(choices=title)
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    phone_number = forms.RegexField(regex=r'^.{10}$',
                                    error_messages={'invalid': "Phone number must be entered \
                                                  in the format: '9999999999'.\
                                                 Up to 10 digits allowed."})
    institute = forms.CharField(max_length=128,
                                help_text='Please write full name of your Institute/Organization')
    department = forms.ChoiceField(help_text='Department you work/study',
                                   choices=department_choices)
    location = forms.CharField(max_length=255, help_text="Place/City")
    state = forms.ChoiceField(choices=states)
    how_did_you_hear_about_us = forms.ChoiceField(choices=source)

    def clean_username(self):
        u_name = self.cleaned_data["username"]
        if u_name.strip(UNAME_CHARS):
            msg = "Only letters, digits, period  are" \
                  " allowed in username"
            raise forms.ValidationError(msg)
        try:
            User.objects.get(username__exact=u_name)
            raise forms.ValidationError("Username already exists.")
        except User.DoesNotExist:
            return u_name

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if pwd.strip(PWD_CHARS):
            raise forms.ValidationError("Only letters, digits and punctuation\
                                        are allowed in password")
        return pwd

    def clean_confirm_password(self):
        c_pwd = self.cleaned_data['confirm_password']
        pwd = self.data['password']
        if c_pwd != pwd:
            raise forms.ValidationError("Passwords do not match")

        return c_pwd

    def clean_email(self):
        user_email = self.cleaned_data['email']
        if User.objects.filter(email=user_email).exists():
            raise forms.ValidationError("This email already exists")
        return user_email

    def save(self):
        u_name = self.cleaned_data["username"]
        u_name = u_name.lower()
        pwd = self.cleaned_data["password"]
        email = self.cleaned_data["email"]
        new_user = User.objects.create_user(u_name, email, pwd)
        new_user.first_name = self.cleaned_data["first_name"]
        new_user.last_name = self.cleaned_data["last_name"]
        new_user.save()

        cleaned_data = self.cleaned_data
        new_profile = Profile(user=new_user)
        new_profile.institute = cleaned_data["institute"]
        new_profile.department = cleaned_data["department"]
        new_profile.phone_number = cleaned_data["phone_number"]
        new_profile.location = cleaned_data["location"]
        new_profile.title = cleaned_data["title"]
        new_profile.state = cleaned_data["state"]
        new_profile.how_did_you_hear_about_us = cleaned_data["how_did_you_hear_about_us"]
        new_profile.activation_key = generate_activation_key(new_user.username)
        new_profile.key_expiry_time = timezone.now() + timezone.timedelta(days=1)
        new_profile.save()
        return u_name, pwd, new_profile.activation_key


class UserLoginForm(forms.Form):
    """Creates a form which will allow the user to log into the system."""

    username = forms.CharField(max_length=32,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))

    password = forms.CharField(max_length=32,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        super(UserLoginForm, self).clean()
        try:
            u_name, pwd = self.cleaned_data["username"], \
                          self.cleaned_data["password"]
            user = authenticate(username=u_name, password=pwd)
        except Exception:
            raise forms.ValidationError("Username and/or Password is not entered")
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return user


class WorkshopForm(forms.ModelForm):
    """
    Coordinators will propose a workshop and date 
    """
    errorlist_css_class = 'errorlist'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(WorkshopForm, self).__init__(*args, **kwargs)
        self.fields['tnc_accepted'].label = ""
        self.fields['tnc_accepted'].required = True
        self.fields['workshop_type'].label = "Workshop :"
        self.fields['date'].label = "Workshop Date :"

    class Meta:
        model = Workshop
        exclude = ['status', 'instructor', 'coordinator']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'datepicker form-control', 'placeholder': 'Workshop Date'}),
            'workshop_type': forms.Select(attrs={
                'class': 'form-control'}),
            'tnc_accepted': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CommentsForm(forms.ModelForm):
    """
    Users will post comments on workshops
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(CommentsForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = True
        self.fields['public'].label = "Public"

    class Meta:
        model = Comment
        exclude = ['author', 'created_date', 'workshop']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            })
        }


class WorkshopTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WorkshopTypeForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
            field.field.widget.attrs['placeholder'] = field.label
            field.field.widget.attrs['rows'] = 6

    class Meta:
        model = WorkshopType
        exclude = []


class AttachmentFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttachmentFileForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AttachmentFile
        exclude = ['workshop_type']


class ProfileForm(forms.ModelForm):
    """ profile form for coordinators and instructors """

    class Meta:
        model = Profile
        exclude = ["user", "is_email_verified", "activation_key",
                   "key_expiry_time", "how_did_you_hear_about_us"]

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': "form-control", 'placeholder': "First Name"}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
                    {'class': "form-control", 'placeholder': "Last Name"}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['first_name'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'First Name'}
        )
        self.fields['last_name'].initial = user.last_name
        self.fields['last_name'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'Last Name'}
        )
        self.fields['institute'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'Institute'}
        )
        self.fields['department'].widget.attrs.update(
            {'class': "custom-select"}
        )
        self.fields['title'].widget.attrs.update(
            {'class': "custom-select"}
        )
        self.fields['state'].widget.attrs.update(
            {'class': "custom-select"}
        )
        self.fields['phone_number'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'Phone Number'}
        )
        self.fields['position'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'Position'}
        )
        self.fields['location'].widget.attrs.update(
            {'class': "form-control", 'placeholder': 'Location'}
        )
