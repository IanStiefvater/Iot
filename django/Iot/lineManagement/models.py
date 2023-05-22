from django.db import models
from login.models import user
from django.utils import timezone
from datetime import date

# Create your models here.


class devices(models.Model):
    deviceId = models.IntegerField()
    line = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    dataType = models.CharField(max_length=200)


class lines(models.Model):
    amountDevice = models.IntegerField()
    name = models.CharField(max_length=200)
    dataType = models.CharField(max_length=200)


class device_status(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    shift = models.CharField(max_length=200)
    data = models.BigIntegerField()
    lineid = models.IntegerField(default=0)
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, default="activo")


class lines_maintance(models.Model):
    lineId = models.IntegerField()
    point = models.CharField(max_length=200)
    notes = models.TextField()
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, blank=True)


class device_maintance(models.Model):
    deviceId = models.IntegerField()
    point = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    notes = models.TextField()
    shift = models.CharField(max_length=200)
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, blank=True)

class total_maintenance(models.Model):
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
    userId = models.ForeignKey(user, on_delete=models.CASCADE)
    starTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=255, default="activo")
    notes = models.TextField()


class config(models.Model):
    numLines = models.IntegerField(default=4)


class device_production(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    shift = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    production_data = models.IntegerField()
    created_at = models.CharField(max_length=250)
    date = models.DateField()

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

class graphs(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    shift = models.CharField(max_length=200)
    lineid = models.IntegerField(default=0)
    total_production = models.IntegerField()
    potential_production = models.IntegerField()
    date = models.DateField()

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

