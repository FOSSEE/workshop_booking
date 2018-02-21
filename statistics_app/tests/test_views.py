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

		self.user_two = User.objects.create(
			username='test_user2',
			email='test.user2@gmail.com')

		self.user_two.set_password('pass@123')
		self.user_two.save()

		self.user_two_profile = Profile.objects.create(
			user=self.user_two,
			department='cs',
			institute='IIT',
			position='coordinator',
			phone_number='1122993388',
			is_email_verified=1
			)

	def test_workshop_stats(self):
		settings.SHOW_WORKSHOP_STATS = True
		self.client.login(username=self.user_one, password='pass@123')
		response = self.client.post('/statistics/',
				{
					'from': '2017-01-01',
					'to': '2017-12-31',
					'Download': 'download'
				}
			)
		self.assertEqual(response.status_code, 200)

	def test_workshop_public_stats(self):
		settings.SHOW_WORKSHOP_STATS = True
		response = self.client.post('/statistics/public_stats/',
				{
					'from': '2017-01-01',
					'to': '2017-12-31',
					'View': 'view'
				}
			)
		self.assertEqual(response.status_code, 200)

	def test_profile_stats(self):
		#Coordinator
		self.client.login(username=self.user_two, password='pass@123')
		cresp = self.client.get('/statistics/profile_stats/')
		self.assertEqual(cresp.templates[0].name, 'workshop_app/logout.html')
		#Instructor
		self.client.login(username=self.user_one, password='pass@123')
		response = self.client.get('/statistics/profile_stats/')
		self.assertEqual(response.status_code, 200)
