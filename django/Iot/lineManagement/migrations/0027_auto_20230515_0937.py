# Generated by Django 3.2 on 2023-05-15 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0026_auto_20230505_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='line_status',
            name='timeMaintance',
        ),
        migrations.AddField(
            model_name='device_maintance',
            name='shift',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]