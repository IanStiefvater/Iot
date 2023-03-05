# Generated by Django 3.2 on 2023-03-05 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='device_maintance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deviceID', models.IntegerField()),
                ('point', models.CharField(max_length=200)),
                ('notes', models.TextField()),
                ('starTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='devices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deviceId', models.IntegerField()),
                ('line', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('dataType', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='lines_maintance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lineId', models.IntegerField()),
                ('point', models.CharField(max_length=200)),
                ('notes', models.TextField()),
                ('starTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='line_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lineName', models.CharField(max_length=200)),
                ('shift', models.CharField(max_length=200)),
                ('starTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('status', models.BooleanField(default=1)),
                ('timeMaintance', models.TimeField()),
                ('notes', models.TextField()),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.user')),
            ],
        ),
        migrations.CreateModel(
            name='device_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift', models.CharField(max_length=200)),
                ('data', models.BigIntegerField()),
                ('starTime', models.DateTimeField()),
                ('endTime', models.DateTimeField()),
                ('status', models.BooleanField()),
                ('deviceId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lineManagement.devices')),
            ],
        ),
    ]
