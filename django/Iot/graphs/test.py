import os
import django
import random
from django.utils import timezone
from faker import Faker
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Iot.settings')
django.setup()

from lineManagement.models import  device_production, devices

fake = Faker()


def create_device_production(device):
    # Diccionario para almacenar los deviceID por lineid
    lineid_deviceids = {
        1: [1, 2, 3, 12],
        2: [8, 9, 10, 11],
    }

    start_time = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)

    # Generar una fecha aleatoria sin tiempo para el campo date
    date = start_time.date()

    for _ in range(96):  # Generar 96 snapshots por dispositivo
        shift = random.choice(["Turno 1"])

        # Encuentra el lineid correspondiente al deviceID
        for lineid, deviceids in lineid_deviceids.items():
            if device.id in deviceids:
                break
        else:
            # Si el deviceID no se encuentra en el diccionario, saltar a la siguiente iteración del bucle
            continue

        production_data = random.randint(1, 100)

        # Calcular la hora exacta para created_at
        created_at = start_time + datetime.timedelta(minutes=5 * _)
        created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')

        device_prod = device_production(
            deviceId=device,
            shift=shift,
            lineid=lineid,
            production_data=production_data,
            created_at=created_at_str,
            date=date
        )
        device_prod.save()
        device_prod.set_date_from_status()
        device_prod.save()

        all_devices = devices.objects.all()

        for device in all_devices:
            create_device_production(device)
