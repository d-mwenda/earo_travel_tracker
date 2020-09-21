# Generated by Django 2.2 on 2020-09-21 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('traveler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelerdetails',
            name='is_managed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Line_Manager', to='traveler.TravelerDetails', verbose_name='Line Manager'),
        ),
        migrations.AlterField(
            model_name='travelerdetails',
            name='is_dependant_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Guardian', to='traveler.TravelerDetails'),
        ),
        migrations.AlterField(
            model_name='travelerdetails',
            name='type_of_traveler',
            field=models.CharField(choices=[('Employee', 'Employee'), ('Dependant', 'Consultant'), ('Consultant', 'Consultant'), ('Partners', 'Partners')], max_length=20),
        ),
    ]