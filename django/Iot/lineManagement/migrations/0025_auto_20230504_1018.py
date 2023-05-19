# Generated by Django 3.2 on 2023-05-04 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lineManagement', '0024_merge_0019_auto_20230417_1703_0023_graphs'),
    ]

    operations = [
        migrations.AddField(
            model_name='device_production',
            name='name',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='graphs',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='device_production',
            name='created_at',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='device_production',
            name='production_data',
            field=models.IntegerField(),
        ),
    ]