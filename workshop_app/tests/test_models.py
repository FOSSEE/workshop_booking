from django.test import TestCase
from workshop_app.models import (
                    Profile, User, Workshop, WorkshopType,
                    RequestedWorkshop, BookedWorkshop, ProposeWorkshopDate,
                    Testimonial, ProfileComments
                    )
from datetime import datetime

# Setup for Model Test
def setUpModule():
	'''
		Sets up database 
		demo user as coordinator and test user as instructor
	'''

	demoUser1 = User.objects.create(username='demouser1', 
						email='test.user@gmail.com', password='pass@123')
	demoUser2 = User.objects.create(username='demouser2', 
						email='test.user@gmail.com', password='pass@123')

	testUser1 = User.objects.create(username='testuser1',
						email='test.user@gmail.com',password='pass@123')

	testUser2 = User.objects.create(username='testuser2',
				email='test.user@gmail.com', password='pass@123')

	instructor_profile = Profile.objects.create(user=testUser2, position='instructor',
			department='computer engineering', institute='ace', phone_number='1122334456', 
			title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
			is_email_verified=1)

	coordinator_profile = Profile.objects.create(user=demoUser2, position='coordinator',
			department='IT', institute='iit', phone_number='1122334456',location='powai',
			title='Doctor', how_did_you_hear_about_us='Google', state='IN-MH',
			is_email_verified=1)

	workshoptype1 = WorkshopType.objects.create(workshoptype_name='ISCP',
			workshoptype_description='Introduction to Scientific Computing in\
			Python <br> > Numpy <br> > Matplotlib <br> > iPython <br>',
			workshoptype_duration='1day, 8hours a day')

	requested_workshop = RequestedWorkshop.objects.create(
						requested_workshop_instructor=testUser2,
						requested_workshop_coordinator=demoUser2,
						requested_workshop_title=workshoptype1,
						requested_workshop_date='2017-07-24'
						)
	
	propose_workshop = ProposeWorkshopDate.objects.create(
					proposed_workshop_coordinator=demoUser2,
					proposed_workshop_instructor=testUser2,
					proposed_workshop_title=workshoptype1,
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
			setsup profile for instructor and coordinator
		'''	
		self.testuser1 = User.objects.get(username='testuser1')
		self.demouser1 = User.objects.get(username='demouser1')
		
		self.instructor_profile1 = Profile.objects.create(user=self.testuser1, 
								position='instructor', department='computer engineering', 
								institute='ace', phone_number='1123323344',
								title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
								is_email_verified=1)

		self.coordinator_profile1 = Profile.objects.create(user=self.demouser1, position='coordinator',
								department='IT', institute='iit', phone_number='1122334455',
								title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
								is_email_verified=1)

	def test_profile_model(self):
		self.assertEqual(self.demouser1.email,'test.user@gmail.com')
		self.assertEqual(self.testuser1.email,'test.user@gmail.com')
		self.assertEqual(self.instructor_profile1.position,'instructor')
		self.assertEqual(self.coordinator_profile1.position,'coordinator')
		self.assertEqual(self.coordinator_profile1.location,'powai')
		self.assertEqual(self.instructor_profile1.location,'powai')
		self.assertEqual(self.coordinator_profile1.how_did_you_hear_about_us,'Google')


class WorkshopTypeModelTest(TestCase):
	'''
		This class tests the WorkshopType Model
	'''

	def setUp(self):
		self.workshoptype1 = WorkshopType.objects.create(workshoptype_name='ISCP',
			workshoptype_description='Introduction to Scientific Computing in\
			Python <br> > Numpy <br> > Matplotlib <br> > iPython <br>',
			workshoptype_duration='1day, 8hours a day')

		self.workshoptype2 = WorkshopType.objects.create(workshoptype_name='Basic Python',
			workshoptype_description='Basic Python <br> > DataTypes <br> \
			> Conditions <br> > Loops <br> > Functions'
			,workshoptype_duration='3days, 8hours a day')

	def test_workshoptype_model(self):
		self.assertEqual(self.workshoptype2.workshoptype_duration,'3days, 8hours a day')
		self.assertEqual(self.workshoptype1.workshoptype_name, 'ISCP')


class WorkshopModelTest(TestCase):
	'''
		This class tests the Workshop Model
	'''

	def setUp(self):
		self.testuser2 = User.objects.get(username='testuser2')
		self.instructor_profile = Profile.objects.get(user=self.testuser2)
		self.workshoptype = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.workshop = Workshop.objects.create(workshop_instructor=self.testuser2,
										workshop_title=self.workshoptype,
			recurrences='RRULE:FREQ=WEEKLY;UNTIL=20170629T183000Z;BYDAY=TH')
		
	def test_workshop_model(self):
		self.assertEqual(self.workshop.workshop_title.workshoptype_name,'ISCP' )
		self.assertEqual(self.workshop.recurrences.rrules[0].__dict__['freq'],2)
		

class RequestedWorkshopModelTest(TestCase):
	'''
		This class tests the RequestedWorkshop Model
	'''

	def setUp(self):
		self.testuser2 = User.objects.get(username='testuser2')
		self.demouser2 = User.objects.get(username='demouser2')
		self.workshoptype = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.requestedworkshop = RequestedWorkshop.objects.create(
						requested_workshop_instructor=self.testuser2,
						requested_workshop_coordinator=self.demouser2,
						requested_workshop_title=self.workshoptype,
						requested_workshop_date='2017-05-24'
						)

	def test_requestedworkshop_model(self):
		self.assertEqual(self.requestedworkshop.requested_workshop_date, '2017-05-24')
		self.assertEqual(self.requestedworkshop.status, 'Pending')


class ProposedWorkshopDateModelTest(TestCase):
	'''
		This class tests the ProposeWorkshopDate Model
	'''

	def setUp(self):
		self.testuser2 = User.objects.get(username='testuser2')
		self.demouser2 = User.objects.get(username='demouser2')
		self.workshoptype = WorkshopType.objects.get(workshoptype_name='ISCP')
		self.propose_workshop = ProposeWorkshopDate.objects.create(
					proposed_workshop_coordinator=self.demouser2,
					proposed_workshop_instructor=self.testuser2,
					proposed_workshop_title=self.workshoptype,
					proposed_workshop_date='2017-06-06',
					condition_one=1,
					condition_two=1,
					condition_three=1
					)

	def test_proposedworkshopdate_model(self):
		self.assertEqual(self.propose_workshop.proposed_workshop_title.workshoptype_name,'ISCP')
		self.assertEqual(self.propose_workshop.condition_three, 1)
		self.assertEqual(self.propose_workshop.status, 'Pending')

class BookedWorkshopModelTest(TestCase):
	'''
		This class tests the BookedWorkshop Model
	'''

	def setUp(self):
		self.requestedworkshop = RequestedWorkshop.objects.get(requested_workshop_date='2017-07-24')
		self.propose_workshop = ProposeWorkshopDate.objects.get(proposed_workshop_date='2017-07-06')
		self.bwr = BookedWorkshop.objects.create(booked_workshop_requested=self.requestedworkshop)
		self.bwp = BookedWorkshop.objects.create(booked_workshop_proposed=self.propose_workshop)

	def test_bookedworkshop_model(self):
		self.assertEqual(self.bwp.booked_workshop_proposed.condition_one,1)
		self.assertEqual(self.bwr.booked_workshop_requested.requested_workshop_title.workshoptype_name,
						'ISCP' )



class TestimonialModelTest(TestCase):
	'''
	This class tests the Testimonial Model
	'''

	def setUp(self):
		self.testimonial_one = Testimonial.objects.create(
						name='ABC XYZ',
						institute='VIDYA GHAR',
						department='computer engineering',
						message='Lorem ipsum dolor sit amet, consectetur \
				tempor incididunt ut labore et dolore magna aliqua\
				quis nostrud exercitation ullamco laboris nisi ut \
				consequat. Duis aute irure dolor in reprehenderit in voluptat\
				cillum dolore eu fugiat nulla pariatur. Excepteur sint \
				proident, sunt in culpa qui officia deserunt mollit anim'
				)
		
	def test_testimonials_model(self):
		self.assertEqual(self.testimonial_one.name, 'ABC XYZ')
		self.assertEqual(self.testimonial_one.department, 'computer engineering')
		self.assertEqual(self.testimonial_one.institute, 'VIDYA GHAR')
		self.assertEqual(self.testimonial_one.message, 'Lorem ipsum dolor sit amet, consectetur \
				tempor incididunt ut labore et dolore magna aliqua\
				quis nostrud exercitation ullamco laboris nisi ut \
				consequat. Duis aute irure dolor in reprehenderit in voluptat\
				cillum dolore eu fugiat nulla pariatur. Excepteur sint \
				proident, sunt in culpa qui officia deserunt mollit anim')



class ProfileCommentsTest(TestCase):
	'''
	This class tests the ProfileComments Model
	'''

	def setUp(self):
		self.coordinator_prof = User.objects.get(username='demouser2')
		self.instructor_prof = User.objects.get(username='testuser2')

		self.comment = ProfileComments.objects.create(
			coordinator_profile=self.coordinator_prof,
			comment="This is a test comment",
			instructor_profile=self.instructor_prof,
			created_date='2017-06-06 12:00:12'
		)

	def test_profilecomments_model(self):
		self.assertEqual(self.coordinator_prof.email, 'test.user@gmail.com')
		self.assertEqual(self.comment.comment, 'This is a test comment')