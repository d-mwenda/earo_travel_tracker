# Generated by Django 2.2 on 2020-09-30 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0009_auto_20200930_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tripitinerary',
            name='leg_status',
            field=models.CharField(default='Incomplete', max_length=10),
        ),
    ]