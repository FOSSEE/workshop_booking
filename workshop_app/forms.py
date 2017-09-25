from django import forms
from django.utils import timezone
from .models import (
                    Profile, User, Workshop, WorkshopType, 
                    RequestedWorkshop, BookedWorkshop, ProposeWorkshopDate
                    )
from string import punctuation, digits
try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .send_mails import generate_activation_key


UNAME_CHARS = letters + "._" + digits
PWD_CHARS = letters + punctuation + digits

position_choices = (
    ("coordinator", "Coordinator"),
    ("instructor", "Instructor")
    )

department_choices = (
    ("computer engineering", "Computer Science"),
    ("information technology", "Information Technology"),
    ("civil engineering", "Civil Engineering"),
    ("electrical engineering", "Electrical Engineering"),
    ("mechanical engineering", "Mechanical Engineering"),
    ("chemical engineering", "Chemical Engineering"),
    ("aerospace engineering", "Aerospace Engineering"),
    ("biosciences and bioengineering", "Biosciences and  BioEngineering"),
    ("electronics", "Electronics"),
    ("energy science and engineering", "Energy Science and Engineering"),
    ("others", "Others"),
    )

title = (
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
    ("Shriman", "Shri"),
    ("Shrimati", "Smt"),
    ("Kumari", "Ku"),
    ("Mr", "Mr."),
    ("Mrs", "Mrs."),
    ("Miss", "Ms."),
    ("other", "Other"),
    )

source = (
    ("FOSSEE Email", "FOSSEE Email"),
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
    ("Others", "Others"),
    )

states = (
    ("IN-AP",	"Andhra Pradesh"),	
    ("IN-AR",	"Arunachal Pradesh"),	
    ("IN-AS",	"Assam"),	
    ("IN-BR",	"Bihar"),	
    ("IN-CT",	"Chhattisgarh"),	
    ("IN-GA",	"Goa"),	
    ("IN-GJ",	"Gujarat"),	
    ("IN-HR",	"Haryana"),	
    ("IN-HP",	"Himachal Pradesh"),	
    ("IN-JK",	"Jammu and Kashmir"),	
    ("IN-JH",	"Jharkhand"),	
    ("IN-KA",	"Karnataka"),	
    ("IN-KL",	"Kerala"),	
    ("IN-MP",	"Madhya Pradesh"),	
    ("IN-MH",	"Maharashtra"),	
    ("IN-MN",	"Manipur"),	
    ("IN-ML",	"Meghalaya"),	
    ("IN-MZ",	"Mizoram"),	
    ("IN-NL",	"Nagaland"),	
    ("IN-OR",	"Odisha"),	
    ("IN-PB",	"Punjab"),	
    ("IN-RJ",	"Rajasthan"),	
    ("IN-SK",	"Sikkim"),	
    ("IN-TN",	"Tamil Nadu"),	
    ("IN-TG",	"Telangana"),	
    ("IN-TR",	"Tripura"),
    ("IN-UT",	"Uttarakhand"),	
    ("IN-UP",	"Uttar Pradesh"),	
    ("IN-WB",	"West Bengal"),
    ("IN-AN",	"Andaman and Nicobar Islands"),	
    ("IN-CH",	"Chandigarh"),	
    ("IN-DN",	"Dadra and Nagar Haveli"),	
    ("IN-DD",	"Daman and Diu"),	
    ("IN-DL",	"Delhi"),	
    ("IN-LD",	"Lakshadweep"),	
    ("IN-PY",	"Puducherry")	
    )


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
    confirm_password = forms.CharField\
                       (max_length=32, widget=forms.PasswordInput())
    title = forms.ChoiceField(choices=title)
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    phone_number = forms.RegexField(regex=r'^.{10}$', 
                                error_messages={'invalid':"Phone number must be entered \
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
            msg = "Only letters, digits, period  are"\
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
        #new_profile.position = cleaned_data["position"]
        new_profile.phone_number = cleaned_data["phone_number"]
        new_profile.location = cleaned_data["location"]
        new_profile.title = cleaned_data["title"]
        new_profile.state = cleaned_data["state"]
        new_profile.how_did_you_hear_about_us = cleaned_data["how_did_you_hear_about_us" ]
        new_profile.activation_key = generate_activation_key(new_user.username)
        new_profile.key_expiry_time = timezone.now() + \
                                    timezone.timedelta(days=1)
        new_profile.save()
        key = Profile.objects.get(user=new_user).activation_key
        return u_name, pwd, key

class UserLoginForm(forms.Form):
    """Creates a form which will allow the user to log into the system."""

    username = forms.CharField(max_length=32,
            widget=forms.TextInput(attrs={'placeholder': 'your username'}))

    password = forms.CharField(max_length=32,
            widget=forms.PasswordInput(attrs={'placeholder': 'your password'}))

    def clean(self):
        super(UserLoginForm, self).clean()
        try:
            u_name, pwd = self.cleaned_data["username"],\
                          self.cleaned_data["password"]
            user = authenticate(username=u_name, password=pwd)
        except Exception:
            raise forms.ValidationError\
                        ("Username and/or Password is not entered")
        if not user:
            raise forms.ValidationError("Invalid username/password")
        return user

class ProfileForm(forms.ModelForm):
    """ profile form for coordinator and instructor """

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'institute', 'department',
                ]

    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name

class CreateWorkshop(forms.ModelForm):
    """
    Instructors can create Workshops based on the Types 
    of available workshops.
    """

    def __init__( self, *args, **kwargs ):
        kwargs.setdefault('label_suffix', '')
        super(CreateWorkshop, self).__init__( *args, **kwargs )
        self.fields['recurrences'].label = " " #the trick to hide field :)

    class Meta:
        model = Workshop
        fields = ['workshop_title', 'recurrences']

    
class ProposeWorkshopDateForm(forms.ModelForm):
    """
    Coordinators will propose a workshop and date 
    """ 
    errorlist_css_class = 'errorlist'
    def __init__( self, *args, **kwargs ):
        kwargs.setdefault('label_suffix', '')
        super(ProposeWorkshopDateForm, self).__init__(*args, **kwargs)
        self.fields['condition_one'].label = ""
        self.fields['condition_one'].required = True
        self.fields['condition_two'].label = ""
        self.fields['condition_two'].required = True
        self.fields['condition_three'].label = ""
        self.fields['condition_three'].required = True
        self.fields['proposed_workshop_title'].label = "Workshop :"
        self.fields['proposed_workshop_date'].label = "Workshop Date :"
        
    class Meta:
        model = ProposeWorkshopDate
        exclude = ['status', 'proposed_workshop_instructor', 
                    'proposed_workshop_coordinator']
        widgets = {
            'proposed_workshop_date': forms.DateInput(attrs={
                'class':'datepicker'})
            }
