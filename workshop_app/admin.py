import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import (
    Profile, WorkshopType,
    Workshop,
    Testimonial, Comment, Banner, AttachmentFile
)

try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io


# Custom Classes
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'institute', 'location', 'department',
                    'phone_number', 'position']
    list_filter = ['position', 'department']
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        openfile = string_io()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=profile_data.csv'
        writer = csv.writer(response)
        writer.writerow(['email_id', 'title', 'username', 'first_name', 'last_name',
                         'institute', 'location', 'department',
                         'phone_number', 'position'])
        for q in queryset:
            writer.writerow([q.user.email, q.title, q.user, q.user.first_name,
                             q.user.last_name, q.institute,
                             q.location, q.department, q.phone_number,
                             q.position])

        openfile.seek(0)
        response.write(openfile.read())
        return response

    download_csv.short_description = "Download CSV file for selected stats."


class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['workshop_type', 'instructor', 'date', 'status', 'coordinator']
    list_filter = ['workshop_type', 'date']
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        openfile = string_io()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=workshop_data.csv'
        writer = csv.writer(response)
        writer.writerow(['workshop_type', 'date', 'instructor', 'coordinator', 'status'])

        for q in queryset:
            writer.writerow([q.title, q.date, q.instructor, q.coordinator, q.status])

        openfile.seek(0)
        response.write(openfile.read())
        return response

    download_csv.short_description = "Download CSV file for selected stats."


class AttachmentFileInline(admin.TabularInline):
    model = AttachmentFile


class WorkshopTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration']
    list_filter = ['name']
    actions = ['download_csv']
    inlines = [AttachmentFileInline]

    def download_csv(self, request, queryset):
        openfile = string_io()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename=workshoptype_data.csv'
        writer = csv.writer(response)
        writer.writerow(['name', 'duration'])

        for q in queryset:
            writer.writerow([q.name, q.duration])

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
        response['Content-Disposition'] = 'attachment;filename=testimonials_data.csv'
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


class CommentAdmin(admin.ModelAdmin):
    list_display = ['workshop', 'comment', 'created_date', 'author', 'public']
    list_filter = ['workshop', 'author', 'created_date', 'public']


# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(WorkshopType, WorkshopTypeAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Banner)
admin.site.register(AttachmentFile)
