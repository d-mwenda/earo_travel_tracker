# Generated by Django 2.2 on 2020-10-27 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('traveler', '0007_auto_20201027_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travelerdetails',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='traveler.DepartmentsModel'),
        ),
    ]
