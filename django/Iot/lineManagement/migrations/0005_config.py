# Generated by Django 3.2 on 2023-03-07 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0004_auto_20230305_1837'),
    ]

    operations = [
        migrations.CreateModel(
            name='config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numLines', models.IntegerField(default=4)),
            ],
        ),
    ]