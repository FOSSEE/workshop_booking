# Generated by Django 3.0.7 on 2020-07-27 18:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('workshop_app', '0012_auto_20200727_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshop',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
    ]
