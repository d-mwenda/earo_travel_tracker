# Generated by Django 2.2 on 2021-01-26 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trip', '0004_auto_20210122_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tripapproval',
            name='approver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='traveler.Approver', verbose_name='Approved by'),
        ),
    ]