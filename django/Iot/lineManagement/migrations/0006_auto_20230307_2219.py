# Generated by Django 3.2 on 2023-03-08 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0005_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='device_maintance',
            name='lineid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='device_status',
            name='lineid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='line_status',
            name='amountDevices',
            field=models.IntegerField(default=0),
        ),
    ]
