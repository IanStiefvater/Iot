from lineManagement.models import devices, device_production, lines, config_shift
from django.db.models import F, ExpressionWrapper, fields, DateTimeField
from datetime import timedelta, timezone
from django.db import connection
from dateutil import tz
from datetime import datetime, time
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models.functions import Now, Trunc
import math


def dataGraph(linename):
    try:
        # Realiza la consulta para obtener el dispositivo por linename
        device = devices.objects.filter(line=linename)
        timezone = tz.gettz("America/Argentina/Mendoza")
        hora_actual = datetime.now(timezone)
        hora_actual_str = hora_actual.strftime("%H:%M")
        date = hora_actual.date()
        turno = config_shift.objects.filter(
            startTime__lte=hora_actual_str, endTime__gte=hora_actual_str
        ).first()

        # Si se encontró

        # Devuelve el nombre del turno en una respuesta JSON

        initial_date = datetime.combine(date, turno.startTime)
        final_date = datetime.combine(date, turno.endTime)

        # Convierte los objetos datetime en cadenas
        initial_date_str = initial_date.strftime("%Y-%m-%d %H:%M:%S")
        final_date_str = final_date.strftime("%Y-%m-%d %H:%M:%S")

        # Realiza la consulta para obtener la línea de dispositivo
        line = lines.objects.get(name=linename)

        device = devices.objects.filter(line=linename)
        production = []
        time = []
        final_result = {}

        # Luego, realiza la consulta de device_production usando la línea del dispositivo y el rango de fechas

        # Verifica si se encontraron dispositivos
        if device.exists():
            # Convierte los resultados en una lista de diccionarios
            device_id = [dev.id for dev in device]
            device_names = [dev.name for dev in device]
            device_names.insert(0, "Hora")
            count = 0
            devices_name = []
            for a in device_id:
                count += 1
                device_productions = device_production.objects.filter(
                    lineid=line.id,
                    deviceId_id_id=a,
                    created_at__range=(initial_date_str, final_date_str),
                ).order_by("id")

                # Inicializa listas para las producciones y tiempos de este dispositivo específico
                device_production_data = []
                device_production_time = []
                query_devices_names = devices.objects.filter(id=a).first()
                devices_name.append(query_devices_names.name)

                for production in device_productions:
                    # Convert the 'created_at' attribute to a datetime object
                    created_time = production.created_at.rsplit(".", 1)[0]
                    created_at_datetime = datetime.strptime(
                        created_time, "%Y-%m-%d %H:%M:%S"
                    )

                    # Add the production data and time to the corresponding lists
                    device_production_data.append(production.production_data)
                    device_production_time.append(created_at_datetime)

                # Add the lists of productions and times for this device to the final JSON
                final_result[f"device_{a}_production_data"] = device_production_data
                final_result[f"device_{a}_production_time"] = device_production_time

        # Imprimir el resultado como un JSON
        import json

        reponse = {
            **{key: value for key, value in final_result.items()},
            "quantity": count,
            "devices_name": devices_name,
            # "prueba": final_result,
        }
        # Devuelve los datos como JSON
        # response_data = {"response": result_list}

        # Convertir la lista de producciones en un JSON
        # production_data_list = list(production)
        return JsonResponse(reponse)

    except line.DoesNotExist:
        # Maneja el caso en que no se encuentra un dispositivo con el linename especificado
        return JsonResponse({"error": "Device not found"}, status=404)
