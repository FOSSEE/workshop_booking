# Generated by Django 3.0.7 on 2020-07-27 17:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import workshop_app.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workshop_app', '0010_auto_20190926_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachments', models.FileField(help_text='Please upload workshop documents one by one,                     ie.workshop schedule, instructions etc.                     Please Note: Name of Schedule file should be similar to                     WorkshopType Name', upload_to=workshop_app.models.attachments)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('public', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='profilecomments',
            name='coordinator_profile',
        ),
        migrations.RemoveField(
            model_name='profilecomments',
            name='instructor_profile',
        ),
        migrations.RemoveField(
            model_name='proposeworkshopdate',
            name='proposed_workshop_coordinator',
        ),
        migrations.RemoveField(
            model_name='proposeworkshopdate',
            name='proposed_workshop_instructor',
        ),
        migrations.RemoveField(
            model_name='proposeworkshopdate',
            name='proposed_workshop_title',
        ),
        migrations.RemoveField(
            model_name='requestedworkshop',
            name='requested_workshop_coordinator',
        ),
        migrations.RemoveField(
            model_name='requestedworkshop',
            name='requested_workshop_instructor',
        ),
        migrations.RemoveField(
            model_name='requestedworkshop',
            name='requested_workshop_title',
        ),
        migrations.RenameField(
            model_name='workshop',
            old_name='workshop_instructor',
            new_name='coordinator',
        ),
        migrations.RenameField(
            model_name='workshoptype',
            old_name='workshoptype_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='workshoptype',
            old_name='workshoptype_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='workshop',
            name='recurrences',
        ),
        migrations.RemoveField(
            model_name='workshop',
            name='workshop_title',
        ),
        migrations.RemoveField(
            model_name='workshoptype',
            name='workshoptype_attachments',
        ),
        migrations.RemoveField(
            model_name='workshoptype',
            name='workshoptype_duration',
        ),
        migrations.AddField(
            model_name='workshop',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workshop',
            name='instructor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workshop_app_workshop_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='workshop',
            name='status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Accepted'), (2, 'Deleted')], default=0),
        ),
        migrations.AddField(
            model_name='workshop',
            name='tnc_accepted',
            field=models.BooleanField(default=False, help_text='I accept the terms and conditions'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workshop',
            name='workshop_type',
            field=models.ForeignKey(default=1, help_text='Select the type of workshop.', on_delete=django.db.models.deletion.CASCADE, to='workshop_app.WorkshopType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workshoptype',
            name='duration',
            field=models.PositiveIntegerField(default=1, help_text='Please enter duration in days', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workshoptype',
            name='terms_and_conditions',
            field=models.TextField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message="Phone number must be entered                 in the format: '9999999999'.                Up to 10 digits allowed.", regex='^.{10}$')]),
        ),
        migrations.DeleteModel(
            name='BookedWorkshop',
        ),
        migrations.DeleteModel(
            name='ProfileComments',
        ),
        migrations.DeleteModel(
            name='ProposeWorkshopDate',
        ),
        migrations.DeleteModel(
            name='RequestedWorkshop',
        ),
        migrations.AddField(
            model_name='comment',
            name='workshop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop_app.Workshop'),
        ),
        migrations.AddField(
            model_name='attachmentfile',
            name='workshop_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workshop_app.WorkshopType'),
        ),
    ]
