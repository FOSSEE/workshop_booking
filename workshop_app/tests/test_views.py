from workshop_app.views import view_profile, user_login, edit_profile
from django.test import TestCase
from workshop_app.models import Profile, User, Workshop, WorkshopType,\
					RequestedWorkshop, BookedWorkshop, ProposeWorkshopDate,\
					has_profile
from datetime import datetime
from json import dumps
from django.test import Client
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from workshop_app.forms import CreateWorkshop
from django.conf import settings


class TestProfile(TestCase):
	def setUp(self):
		self.client = Client()

		self.user1 = User.objects.create(
			username='demo_test_user1',
			password='pass@123',
			email='test.user@gmail.com')

		self.user2 = User.objects.create(
			username='demo_test_user2',
			email='test.user@gmail.com')

		self.user2.set_password('pass@123')
		self.user2.save()

		self.user2_profile = Profile.objects.create(
			user=self.user2,
			department='Computer Engineering',
			institute='ace',
			title='Doctor',
			position='instructor',
			phone_number='1122993388',
			location='mumbai',
			how_did_you_hear_about_us='Google',
			state='IN-MH',
			is_email_verified=1
			)

	def test_has_profile_for_user_without_profile(self):
		"""
		If no profile exists for user passed as argument return False
		"""
		has_profile_status = has_profile(self.user1)
		self.assertFalse(has_profile_status)

	def test_has_profile_for_user_with_profile(self):
		"""
		If profile exists for user passed as argument return True
		"""
		has_profile_status = has_profile(self.user2)
		self.assertTrue(has_profile_status)

	def test_view_profile_denies_anonymous(self):
		"""
		If not logged in redirect to login page
		"""
		response = self.client.get(reverse(view_profile), follow=True)
		redirect_destination = '/login/?next=/view_profile/'
		self.assertTrue(response.status_code,200)
		self.assertRedirects(response, redirect_destination)

	def test_edit_profile_get(self):
		"""
		GET request to edit profile should display profile form
		"""

		self.client.login(username=self.user2, password='pass@123')
		response = self.client.get(reverse(edit_profile))
		user_profile = User.objects.get(id=self.user2.id)
		profile = Profile.objects.get(user=user_profile)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(profile.institute, 'ace')
		self.client.logout()

	def test_edit_profile_post(self):

		self.client.login(username=self.user2, password='pass@123')
		response = self.client.post('/edit_profile/',
			{
				'first_name': 'demo_test',
				'last_name': 'user2',
				'institute': 'IIT',
				'department': 'aerospace engineering'
					})
	
		updated_profile_user = User.objects.get(id=self.user2.id)
		updated_profile = Profile.objects.get(user=updated_profile_user)
		self.assertEqual(updated_profile.institute, 'IIT')
		self.assertEqual(updated_profile.department, 'aerospace engineering')
		self.assertEqual(updated_profile.position, 'instructor')
		self.assertEqual(response.status_code, 200)
		# self.assertTemplateUsed(response, 'workshop_app/profile_updated.html')

	def test_register_page(self):
		self.client.get('/register/')
		self.register_response = self.client.post('/register/',
			data={
			'username':'testuser',
			'email':'test@user.com',
			'password':'ABCD@123*',
			'confirm password':'ABCD@123*',
			'first name':'testor',
			'last name':'user',
			'phone number': 1234567890,
			'institute':'IIT',
			'location':'mumbai',
			'state': (2),
			'department':(2)})

		self.assertEqual(self.register_response.status_code,200)


class TestWorkshopCreation(TestCase):
	def setUp(self):
		'''
		demo user as coordinator and test user as instructor
		'''
		self.superuser = User.objects.create_superuser(
			username='admin',
			password='pass@123',
			email='test.user@gmail.com')

		self.mod_group = Group.objects.create(name='instructor')

		self.user_one = User.objects.create(
			username='test_user1',
			email='test.user@gmail.com')

		self.user_one.set_password('pass@123')
		self.user_one.save()

		self.user_one_profile = Profile.objects.create(
			user=self.user_one,
			department='computer engineering',
			title='Doctor',
			institute='IIT',
			position='instructor',
			how_did_you_hear_about_us='Google',
			phone_number='1122993388',
			location='mumbai',
			state='IN-MH',
			is_email_verified=1
			)

		#Add user_one in instructor group and give required permissions
		self.mod_group.user_set.add(self.user_one)
		self.permission = (Permission.objects.all())
		self.user_one.user_permissions.add(self.permission[44])
		self.user_one.user_permissions.add(self.permission[43])
		self.user_one.user_permissions.add(self.permission[42])
		
		self.user_two = User.objects.create(
			username='demo_user2',
			email='test.user@gmail.com')

		self.user_two.set_password('pass@123')
		self.user_two.save()

		self.user_two_profile = Profile.objects.create(
			user=self.user_two,
			department='computer engineering',
			institute='ace',
			position='coordinator',
			title='Mr',
			how_did_you_hear_about_us='Google',
			location='mumbai',
			state='IN-MH',
			phone_number='1122993388',
			is_email_verified=1
			)

		self.workshoptype = WorkshopType.objects.create(workshoptype_name='ISCP', workshoptype_description='Introduction to Scientific Computing in Python <br>\
				> Numpy <br> > Matplotlib <br> > iPython <br>', workshoptype_duration='1days, 8hours a day')

	def test_create_workshoptype_superuser(self):
		self.client.login(username=self.superuser, password='pass@123')
		self.client.post(('/admin/workshop_app/workshoptype/add/'),
			data={
				'workshoptype_name': 'Basic Python',
				'workshoptype_description': 'Basics of Python <br>\
							> Conditions <br> > Datatypes <br> > Loops <br>',
				'workshoptype_duration': '3days, 8hours a day'
				})
		self.workshoptype_one = WorkshopType.objects.get(workshoptype_name='Basic Python')
		self.assertEqual(self.workshoptype_one.workshoptype_name, 'Basic Python')
		self.assertEqual(self.workshoptype_one.workshoptype_duration, '3days, 8hours a day')
		self.client.logout()
		
	def test_create_workshop_instructor(self):
		self.client.login(username=self.user_one, password='pass@123')
		self.client.post('/create_workshop/',
			{
				'workshop_title' : self.workshoptype.id,
				'recurrences' : 'RRULE:FREQ=WEEKLY;UNTIL=20170924T183000Z;BYDAY=WE;'
			})
		self.workshop = Workshop.objects.get(workshop_instructor=self.user_one)
		self.assertEqual(str(self.workshop.workshop_title), 'ISCP 1days, 8hours a day')
		self.client.logout()


	def test_propose_workshop_coordinator(self):
		self.client.login(username=self.user_two, password='pass@123')
		self.client.post('/propose_workshop/',
			{
				'condition_one': 1,
				'condition_two': 1,
				'condition_three': 1,
				'proposed_workshop_title': self.workshoptype.id,
				'proposed_workshop_date': '2017-06-06'
			})
		self.proposed_workshop = ProposeWorkshopDate.objects.get(proposed_workshop_date='2017-06-06')
		self.assertEqual(str(self.proposed_workshop.proposed_workshop_title),
						'ISCP 1days, 8hours a day')
		self.client.logout()


class TestWorkshopDashboard(TestCase):
	def setUp(self):
		self.superuser = User.objects.create_superuser(
			username='admin',
			password='pass@123',
			email='test.user@gmail.com')

		self.mod_group = Group.objects.create(name='instructor')

		self.user_one = User.objects.create(
			username='test_user1',
			email='test.user@gmail.com')

		self.user_one.set_password('pass@123')
		self.user_one.save()

		self.user_one_profile = Profile.objects.create(
			user=self.user_one,
			department='cs',
			institute='IIT',
			position='instructor',
			phone_number='1122993388',
			how_did_you_hear_about_us='Google',
			location='mumbai',
			state='IN-MH',
			title='Mr',
			is_email_verified=1
			)

		#Add user_one in instructor group and give required permissions
		self.mod_group.user_set.add(self.user_one)
		self.permissions = Permission.objects.all()
		self.user_one.user_permissions.add(self.permissions[44])
		self.user_one.user_permissions.add(self.permissions[43])
		self.user_one.user_permissions.add(self.permissions[42])
		
		self.user_two = User.objects.create(
			username='demo_user2',
			email='test.user@gmail.com')

		self.user_two.set_password('pass@123')
		self.user_two.save()

		self.user_two_profile = Profile.objects.create(
			user=self.user_two,
			department='cs',
			institute='ace',
			position='coordinator',
			phone_number='1122993388',
			is_email_verified=1
			)

		self.workshoptype = WorkshopType.objects.create(workshoptype_name='ISCP', workshoptype_description='Introduction to Scientific Computing in Python <br>\
				> Numpy <br> > Matplotlib <br> > iPython <br>', workshoptype_duration='1days, 8hours a day')

		self.workshop = Workshop.objects.create(workshop_instructor=self.user_one,
						workshop_title=self.workshoptype,
						recurrences='RRULE:FREQ=WEEKLY;UNTIL=20170624T183000Z;BYDAY=WE;'
						)


class TestStaticPages(TestCase):

	def test_register(self):
		response = self.client.get('/register/')
		self.assertEqual(response.status_code, 200)

	def test_faq(self): 
		response = self.client.get('/faq/')
		self.assertEqual(response.status_code, 200)

	def test_how_to_participate(self):
		response = self.client.get('/how_to_participate/')
		self.assertEqual(response.status_code, 200)

	def test_view_workshoptype_list(self):
		response = self.client.get('/view_workshoptype_list/')
		self.assertEqual(response.status_code, 200)

	def test_view_self_workshop(self):
		response = self.client.get('/self_workshop/')
		self.assertEqual(response.status_code, 200)


class TestWorkshopStats(TestCase):
	def setUp(self):
		'''
		test user as instructor
		'''
		self.superuser = User.objects.create_superuser(
			username='admin',
			password='pass@123',
			email='test.user@gmail.com')

		self.mod_group = Group.objects.create(name='instructor')

		self.user_one = User.objects.create(
			username='test_user1',
			email='test.user@gmail.com')

		self.user_one.set_password('pass@123')
		self.user_one.save()

		self.user_one_profile = Profile.objects.create(
			user=self.user_one,
			department='cs',
			institute='IIT',
			position='instructor',
			phone_number='1122993388',
			is_email_verified=1
			)

		#Add user_one in instructor group and give required permissions
		self.mod_group.user_set.add(self.user_one)
		self.permission = (Permission.objects.all())
		self.user_one.user_permissions.add(self.permission[44])
		self.user_one.user_permissions.add(self.permission[43])
		self.user_one.user_permissions.add(self.permission[42])

	def test_workshop_stats(self):
		settings.SHOW_WORKSHOP_STATS = True
		self.client.login(username=self.user_one, password='pass@123')
		response = self.client.post('/workshop_stats/',
				{
					'from': '2017-01-01',
					'to': '2017-12-31',
					'Download': 'download'
				}
			)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.get('Content-Disposition'),'attachment;\
                                filename="records_from_2017-01-01_to_2017-12-31.csv"')
