# Generated by Django 3.2 on 2023-03-05 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device_maintance',
            name='starTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='device_status',
            name='starTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='device_status',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='line_status',
            name='starTime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='lines_maintance',
            name='starTime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
