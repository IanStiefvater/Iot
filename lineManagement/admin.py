from django.contrib import admin
from .models import device_maintenance, lines_maintenance

admin.site.register(device_maintenance)
admin.site.register(lines_maintenance)

# Register your models here.
