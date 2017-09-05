import csv
from django.http import HttpResponse
from django.contrib import admin  
from .models import (
				Profile, WorkshopType, 
				Workshop, ProposeWorkshopDate,
				RequestedWorkshop, BookedWorkshop,
				Testimonial
				)
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io

#Custom Classes 
class ProfileAdmin(admin.ModelAdmin):
	list_display = ['title','user', 'institute','location','department','phone_number','position']
	list_filter = ['position', 'department']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=profile_data.csv'

		writer = csv.writer(response)
		writer.writerow(['title','user', 'institute', 'location','department','phone_number',
						'position'])
		
		for q in queryset:
			writer.writerow([q.title, q.user, q.institute,
							q.location, q.department, q.phone_number,
							q.position])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."


class ProposeWorkshopDateAdmin(admin.ModelAdmin):
	list_display = ['proposed_workshop_title', 'proposed_workshop_date',
					'proposed_workshop_coordinator', 'status',
					'proposed_workshop_instructor']
	list_filter = ['status']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=proposedworkshop_data.csv'

		writer = csv.writer(response)
		writer.writerow(['proposed_workshop_title', 'proposed_workshop_date',
		 				 'proposed_workshop_coordinator', 'status',
		 				 'proposed_workshop_instructor'])
		
		for q in queryset:
			writer.writerow([q.proposed_workshop_title, q.proposed_workshop_date,
							q.proposed_workshop_coordinator, q.status,
							q.proposed_workshop_instructor])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."


class RequestedWorkshopAdmin(admin.ModelAdmin):
	list_display = ['requested_workshop_title',
					'requested_workshop_date',
					'requested_workshop_coordinator',
					'requested_workshop_instructor',
					'status']

	list_filter = ['status']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=requestedworkshop_data.csv'

		writer = csv.writer(response)
		writer.writerow(['requested_workshop_title',
						'requested_workshop_date',
						'requested_workshop_coordinator',
						'requested_workshop_instructor',
						'status'])
		
		for q in queryset:
			writer.writerow([q.requested_workshop_title, 
							q.requested_workshop_date,
							q.requested_workshop_coordinator, 
							q.requested_workshop_instructor,
							q.status])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."


class WorkshopAdmin(admin.ModelAdmin):
	list_display = ['workshop_title','workshop_instructor']
	list_filter = ['workshop_title']


class WorkshopTypeAdmin(admin.ModelAdmin):
	list_display = ['workshoptype_name', 'workshoptype_duration']
	list_filter = ['workshoptype_name']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=workshoptype_data.csv'

		writer = csv.writer(response)
		writer.writerow(['workshoptype_name', 'workshoptype_duration'])
		
		for q in queryset:
			writer.writerow([q.workshoptype_name, q.workshoptype_duration])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."


class TestimonialAdmin(admin.ModelAdmin):
	list_display = ['name', 'department', 'institute']
	list_filter = ['department']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=testimonials_data.csv'

		writer = csv.writer(response)
		writer.writerow(['name', 'department', 'institute'])
		
		for q in queryset:
			writer.writerow([q.name,
							q.department,
							q.institute
							])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."

class BookedWorkshopAdmin(admin.ModelAdmin):
	list_display = ['booked_workshop_requested',
				    'booked_workshop_proposed']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io() 
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=bookedworkshops_data.csv'

		writer = csv.writer(response)
		writer.writerow(['booked_workshop_requested', 
						 'booked_workshop_proposed'])
		
		for q in queryset:
			writer.writerow([q.booked_workshop_requested,
							q.booked_workshop_proposed
							])

		openfile.seek(0)
		response.write(openfile.read())
		return response
	
	download_csv.short_description = "Download CSV file for selected stats."


# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(WorkshopType, WorkshopTypeAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(ProposeWorkshopDate, ProposeWorkshopDateAdmin)
admin.site.register(RequestedWorkshop, RequestedWorkshopAdmin)
admin.site.register(BookedWorkshop, BookedWorkshopAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
