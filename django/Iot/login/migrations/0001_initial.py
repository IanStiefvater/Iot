# Generated by Django 3.2 on 2023-03-05 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
    ]