# Generated by Django 2.2 on 2020-10-27 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('traveler', '0006_auto_20201014_1046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='travelerdetails',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='travelerdetails',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='travelerdetails',
            name='is_dependant_of',
        ),
        migrations.RemoveField(
            model_name='travelerdetails',
            name='last_name',
        ),
    ]