from django.test import TestCase
from .models import (
					Profile, User, Workshop, WorkshopType, 
                    RequestedWorkshop, BookedWorkshop, ProposeWorkshopDate
                    )
from datetime import datetime

# Setup for Model Test
def setUpModule():
	'''
		demo user as coordinator and test user as instructor
	'''

	demoUser1 = User.objects.create(username='demouser1', 
						email='doke.akshen@gmail.com', password='pass@123')
	demoUser2 = User.objects.create(username='demouser2', 
						email='doke.akshen@gmail.com', password='pass@123')

	testUser1 = User.objects.create(username='testuser1',
						email='doke.akshen@gmail.com',password='pass@123')

	testUser2 = User.objects.create(username='testuser2',
				email='doke.akshen@gmail.com', password='pass@123')

	ip = Profile.objects.create(user=testUser2, position='instructor',
			department='cs', institute='ace', phone_number='9930011492',
			is_email_verified=1)

	cp = Profile.objects.create(user=demoUser2, position='coordinator',
			department='IT', institute='iit', phone_number='9930011492',
			is_email_verified=1)

	wt1 = WorkshopType.objects.create(workshoptype_name='ISCP',
			workshoptype_description='Introduction to Scientific Computing in\
			Python <br> > Numpy <br> > Matplotlib <br> > iPython <br>',
			workshoptype_duration='1day, 8hours a day')

	rw = RequestedWorkshop.objects.create(
						requested_workshop_instructor=testUser2,
						requested_workshop_coordinator=demoUser2,
						requested_workshop_title=wt1,
						requested_workshop_date='2017-07-24'
						)
	
	pw = ProposeWorkshopDate.objects.create(
					proposed_workshop_coordinator=demoUser2,
					proposed_workshop_instructor=testUser2,
					proposed_workshop_title=wt1,
					proposed_workshop_date='2017-07-06',
					condition_one=1,
					condition_two=1,
					condition_three=1
					)


def tearDownModule():
    User.objects.all().delete()
    Profile.objects.all().delete()
    ProposeWorkshopDate.objects.all().delete()
    RequestedWorkshop.objects.all().delete()
    WorkshopType.objects.all().delete()

class ProfileModelTest(TestCase):
	'''	
		This class tests the Profile Model
	'''
	def setUp(self):
		'''
			ip is for instructor profile and cp is for coordinator profile
		'''	
		self.testuser1 = User.objects.get(username='testuser1')
		self.demouser1 = User.objects.get(username='demouser1')
		

		self.ip1 = Profile.objects.create(user=self.testuser1, position='instructor',
			department='cs', institute='ace', phone_number='9930011492',
			is_email_verified=1)

		self.cp1 = Profile.objects.create(user=self.demouser1, position='coordinator',
			department='IT', institute='iit', phone_number='9930011492',
			is_email_verified=1)


	def test_profile_model(self):
		self.assertEqual(self.demouser1.email,'doke.akshen@gmail.com')
		self.assertEqual(self.testuser1.email,'doke.akshen@gmail.com')
		self.assertEqual(self.ip1.position,'instructor')
		self.assertEqual(self.cp1.position,'coordinator')


class WorkshopTypeModelTest(TestCase):
	'''
		This class tests the WorkshopType Model
	'''

	def setUp(self):
		self.wt1 = WorkshopType.objects.create(workshoptype_name='ISCP',
			workshoptype_description='Introduction to Scientific Computing in\
			Python <br> > Numpy <br> > Matplotlib <br> > iPython <br>',
			workshoptype_duration='1day, 8hours a day')

		self.wt2 = WorkshopType.objects.create(workshoptype_name='Basic Python',
			workshoptype_description='Basic Python <br> > DataTypes <br> \
			> Conditions <br> > Loops <br> > Functions'
			,workshoptype_duration='3days, 8hours a day')

	def test_workshoptype_model(self):
		self.assertEqual(self.wt2.workshoptype_duration,'3days, 8hours a day')
		self.assertEqual(self.wt1.workshoptype_name, 'ISCP')


class WorkshopTest(TestCase):
	'''
		This class tests the Workshop Model
	'''

	def setUp(self):
		'''
		 w is workshop object
		'''
		self.testuser2 = User.objects.get(username='testuser2')
		self.ip = Profile.objects.get(user=self.testuser2)
		self.wt = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.w = Workshop.objects.create(workshop_instructor=self.testuser2,
										workshop_title=self.wt,
			recurrences='RRULE:FREQ=WEEKLY;UNTIL=20170524T183000Z;BYDAY=WE')

	def test_workshop_model(self):
		self.assertEqual(self.w.workshop_title.workshoptype_name,'ISCP' )

class RequestedWorkshopTest(TestCase):
	'''
		This class tests the RequestedWorkshop Model
	'''

	def setUp(self):
		self.testuser2 = User.objects.get(username='testuser2')
		self.demouser2 = User.objects.get(username='demouser2')
		self.wt = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.rw = RequestedWorkshop.objects.create(
						requested_workshop_instructor=self.testuser2,
						requested_workshop_coordinator=self.demouser2,
						requested_workshop_title=self.wt,
						requested_workshop_date='2017-05-24'
						)

	def test_requestedworkshop_model(self):
		self.assertEqual(self.rw.requested_workshop_date, '2017-05-24')
		self.assertEqual(self.rw.status, 'Pending')


class ProposedWorkshopDateTest(TestCase):
	'''
		This class tests the ProposeWorkshopDate Model
	'''

	def setUp(self):
		self.testuser2 = User.objects.get(username='testuser2')
		self.demouser2 = User.objects.get(username='demouser2')
		self.wt = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.pw = ProposeWorkshopDate.objects.create(
					proposed_workshop_coordinator=self.demouser2,
					proposed_workshop_instructor=self.testuser2,
					proposed_workshop_title=self.wt,
					proposed_workshop_date='2017-06-06',
					condition_one=1,
					condition_two=1,
					condition_three=1
					)

	def test_proposedworkshopdate_model(self):
		self.assertEqual(self.pw.proposed_workshop_title.workshoptype_name,'ISCP')
		self.assertEqual(self.pw.condition_three, 1)
		self.assertEqual(self.pw.status, 'Pending')

class BookedWorkshopTest(TestCase):
	'''
		This class tests the BookedWorkshop Model
	'''

	def setUp(self):
		self.rw = RequestedWorkshop.objects.get(requested_workshop_date='2017-07-24')
		self.pw = ProposeWorkshopDate.objects.get(proposed_workshop_date='2017-07-06')
		self.bwr = BookedWorkshop.objects.create(booked_workshop_requested=self.rw)
		self.bwp = BookedWorkshop.objects.create(booked_workshop_proposed=self.pw)

	def test_bookedworkshop_model(self):
		self.assertEqual(self.bwp.booked_workshop_proposed.condition_one,1)
		self.assertEqual(self.bwr.booked_workshop_requested.requested_workshop_title.workshoptype_name,'ISCP' )

