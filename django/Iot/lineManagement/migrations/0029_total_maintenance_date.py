# Generated by Django 3.2 on 2023-05-15 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0028_total_maintenance'),
    ]

    operations = [
        migrations.AddField(
            model_name='total_maintenance',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]