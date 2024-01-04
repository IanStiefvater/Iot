from django.db import models
from django.utils import timezone
from datetime import date

from login.models import usuarios

# Create your models here.


class devices(models.Model):
    line = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    dataType = models.CharField(max_length=200)


class lines(models.Model):
    amountDevice = models.IntegerField()
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default="activo")


class device_status(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    shift = models.CharField(max_length=200)
    data = models.BigIntegerField()
    lineid = models.IntegerField(default=0)
    status = models.CharField(max_length=255, default="activo")


class optimal_production_device(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    optimal_production = models.IntegerField(default=0)


class device_maintenance(models.Model):
    deviceId = models.IntegerField()
    point = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    notes = models.TextField()
    shift = models.CharField(max_length=200)
    maintenanceSupervisor = models.CharField(
        max_length=200,
        null=True,
    )
    productionsupervisor = models.CharField(
        max_length=200,
        null=True,
    )
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, blank=True)


class config_shift(models.Model):
    name = models.CharField(max_length=200)
    startTime = models.TimeField()
    endTime = models.TimeField()


class lines_maintenance(models.Model):
    deviceId = models.IntegerField()
    point = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    shift = models.CharField(max_length=200)
    totalTime = models.FloatField()
    date = models.DateField(null=True, blank=True)


class line_status(models.Model):
    lineName = models.CharField(max_length=200)
    amountDevices = models.IntegerField(default=0)
    shift = models.CharField(max_length=200)
    userId = models.ForeignKey(usuarios, on_delete=models.CASCADE)
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=255, default="activo")
    notes = models.TextField()


class config(models.Model):
    numLines = models.IntegerField(default=4)


class device_production(models.Model):
    deviceId_id = models.ForeignKey(devices, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    shift = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    production_data = models.IntegerField()
    created_at = models.CharField(max_length=250)
    date = models.DateField()
    temperature = models.FloatField(null=True, blank=True)
    battery_voltage = models.FloatField(null=True, blank=True)
    battery_percentage = models.FloatField(null=True, blank=True)

    def set_date_from_status(self):
        # Obtener el device_status más reciente para este dispositivo
        status = (
            device_status.objects.filter(deviceId=self.deviceId)
            .order_by("-starTime")
            .first()
        )
        if status:
            # Extraer la fecha del campo starTime
            self.date = status.starTime.date()


class total_maintenance(models.Model):
    deviceId = models.IntegerField(null=True)
    point = models.CharField(max_length=255, null=True)
    lineid = models.IntegerField(null=True)
    shift = models.CharField(max_length=255, null=True)
    totalTime = models.FloatField(null=True)
    date = models.DateField(null=True)


class supervisor(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    email = models.CharField(max_length=255, default="no se ha proporcionado un mail")
