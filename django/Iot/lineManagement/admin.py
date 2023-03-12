from django.contrib import admin
from .models import device_maintance, lines_maintance

admin.site.register(device_maintance)
admin.site.register(lines_maintance)

# Register your models here.
