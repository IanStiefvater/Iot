from django.db import models
from django.db import models
from login.models import user

# Create your models here.


class devices (models.Model):
    deviceId = models.IntegerField()
    line = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    dataType = models.CharField(max_length=200)


class device_status(models.Model):
    deviceId = models.ForeignKey(devices, on_delete=models.CASCADE)
    shift = models.CharField(max_length=200)
    data = models.BigIntegerField()
    starTime = models.DateTimeField()
    endTime = models.DateTimeField()
    status = models.BooleanField()


class lines_maintance (models.Model):
    lineId = models.IntegerField()
    point = models.CharField(max_length=200)
    notes = models.TextField()
    starTime = models.DateTimeField()
    endTime = models.DateTimeField()


class device_maintance (models.Model):
    deviceID = models.IntegerField()
    point = models.CharField(max_length=200)
    notes = models.TextField()
    starTime = models.DateTimeField()
    endTime = models.DateTimeField()


class line_status (models.Model):
    lineName = models.CharField(max_length=200)
    shift = models.CharField(max_length=200)
    userId = models.ForeignKey(user, on_delete=models.CASCADE)
    starTime = models.DateTimeField()
    endTime = models.DateTimeField()
    status = models.BooleanField(default=1)
    timeMaintance = models.TimeField(
        auto_now=False, auto_now_add=False)
    notes = models.TextField()
