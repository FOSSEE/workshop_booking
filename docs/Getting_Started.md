# Guide to install and get this website running

### Follow below given Steps to get started
> __NOTE__: Use Python3 
1. Clone this repo.
    > git clone https://github.com/FOSSEE/workshop_booking.git

2. Create a virtual environment and install all the required packages from requirements.txt
    > pip install -r requirements.txt 

3. Make Migrations and Migrate
    > python manage.py makemigrations\
    > python manage.py migrate

4. Create Super User
    > python manage.py createsuperuser

5. Start Server
    > python manage.py runserver

6. Goto admin page and login using superuser credentials
    > localhost:8000/admin

7. Goto Groups and create one group called __instructor__ and give it all permissions.

8. By default when a user registers, he is assigned a coordinator position, using the admin panel set the required users profile position as instructor and add him/her in instructor group along with the required permissions.

9. Under *settings.py* file see to it that all required variables are set then you're good to go!

### Instructor specific steps

1. An instructor can create workshops as per his/her availibility in __Create Workshop__ tab.

2. Instructor can see monthly workshop count, upcoming workshop etc. in Statistics > Workshop Statistics

3. Instructors can view and post comments on coordinator's profile from Profile Statistics or Workshop Status page.


### Coordinator specific steps

1. A coordinator can sent workshop proposal based on his/her convenience under Workshops > Propose a Workshop option.

