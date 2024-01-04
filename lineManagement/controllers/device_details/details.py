import datetime
from lineManagement.models import lines_maintenance, device_production
from datetime import timedelta, timezone
from django.db import connection
from dateutil import tz
from datetime import datetime, time
from django.shortcuts import render


def get_ph_line(lineId):
    timezone = tz.gettz("America/Argentina/Mendoza")
    hora_actual = datetime.now(timezone) - timedelta(hours=1)
    hora_hace_una_hora = hora_actual - timedelta(hours=1)

    # Formatea las fechas y horas como cadenas en el formato deseado
    hora_actual_str = hora_actual.strftime("%Y-%m-%d %H:%M:%S")
    hora_hace_una_hora_str = hora_hace_una_hora.strftime("%Y-%m-%d %H:%M:%S")

    phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE lineid = %s AND created_at BETWEEN %s AND %s"
    params = [lineId, hora_hace_una_hora_str, hora_actual_str]

    with connection.cursor() as cursor:
        cursor.execute(phsql, params)
        result = cursor.fetchone()
        total_production = result[0] if result else 0

    return total_production


def shift_production_line(lineId):
    hora_inicioturno1 = time(0, 0)
    hora_finturno1 = time(7, 59)
    hora_inicioturno2 = time(8, 0)
    hora_finturno2 = time(15, 59)
    hora_inicioturno3 = time(16, 0)
    hora_finturno3 = time(23, 59)

    # Obtén la fecha y hora actual
    timezone = tz.gettz("America/Argentina/Mendoza")
    fecha_actual = datetime.now(timezone)

    # Compara la hora actual con las horas de inicio y fin
    if hora_inicioturno1 <= fecha_actual.time() < hora_finturno1:
        hora_inicioturno1 = fecha_actual.replace(hour=0, minute=0)
        hora_finturno1 = fecha_actual.replace(hour=7, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE  lineid = %s AND created_at BETWEEN %s AND %s"
        params = [lineId, hora_inicioturno1, hora_finturno1]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production

    if hora_inicioturno2 <= fecha_actual.time() < hora_finturno2:
        hora_inicioturno2 = fecha_actual.replace(hour=8, minute=0)
        hora_finturno2 = fecha_actual.replace(hour=15, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND created_at BETWEEN %s AND %s"
        params = [lineId, hora_inicioturno2, hora_finturno2]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production
    if hora_inicioturno3 <= fecha_actual.time() < hora_finturno3:
        hora_inicioturno3 = fecha_actual.replace(hour=16, minute=0)
        hora_finturno1 = fecha_actual.replace(hour=23, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND created_at BETWEEN %s AND %s"
        params = [lineId, hora_inicioturno3, hora_finturno3]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production

    else:
        print("La hora actual no está dentro del rango permitido.")
        return 0


def get_ph(deviceid, lineId):
    timezone = tz.gettz("America/Argentina/Mendoza")
    hora_actual = datetime.now(timezone)
    hora_hace_una_hora = hora_actual - timedelta(hours=1)

    # Formatea las fechas y horas como cadenas en el formato deseado
    hora_actual_str = hora_actual.strftime("%Y-%m-%d %H:%M:%S")
    hora_hace_una_hora_str = hora_hace_una_hora.strftime("%Y-%m-%d %H:%M:%S")

    phsql = "SELECT SUM(production_data) AS total_production, AVG(battery_voltage) AS voltage FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND (created_at BETWEEN %s AND %s)"
    params = [deviceid, lineId, hora_hace_una_hora_str, hora_actual_str]

    with connection.cursor() as cursor:
        cursor.execute(phsql, params)
        result = cursor.fetchone()
        total_production = result[0] if result else 0
        if result[0] is None:
            total_production = 0
        else:
            total_production = result[0]
        voltage = result[1] if result else 0
        if result[1] is None:
            voltage = 0
        else:
            voltage = result[1]
        return total_production, voltage


def shift_production(deviceId, lineId):
    hora_inicioturno1 = time(0, 0)
    hora_finturno1 = time(7, 59)
    hora_inicioturno2 = time(8, 0)
    hora_finturno2 = time(15, 59)
    hora_inicioturno3 = time(16, 0)
    hora_finturno3 = time(23, 59)

    # Obtén la fecha y hora actual
    timezone = tz.gettz("America/Argentina/Mendoza")
    fecha_actual = datetime.now(timezone)

    # Compara la hora actual con las horas de inicio y fin
    if hora_inicioturno1 <= fecha_actual.time() < hora_finturno1:
        hora_inicioturno1 = fecha_actual.replace(hour=0, minute=0)
        hora_finturno1 = fecha_actual.replace(hour=7, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND created_at BETWEEN %s AND %s"
        params = [deviceId, lineId, hora_inicioturno1, hora_finturno1]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production

    if hora_inicioturno2 <= fecha_actual.time() < hora_finturno2:
        hora_inicioturno2 = fecha_actual.replace(hour=8, minute=0)
        hora_finturno2 = fecha_actual.replace(hour=15, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND created_at BETWEEN %s AND %s"
        params = [deviceId, lineId, hora_inicioturno2, hora_finturno2]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production
    if hora_inicioturno3 <= fecha_actual.time() < hora_finturno3:
        hora_inicioturno3 = fecha_actual.replace(hour=16, minute=0)
        hora_finturno1 = fecha_actual.replace(hour=23, minute=59)
        phsql = "SELECT SUM(production_data) AS total_production FROM lineManagement_device_production WHERE deviceId_id_id = %s AND lineid = %s AND created_at BETWEEN %s AND %s"
        params = [deviceId, lineId, hora_inicioturno3, hora_finturno3]
        with connection.cursor() as cursor:
            cursor.execute(phsql, params)
            result = cursor.fetchone()
            total_production = result[0] if result else 0
            return total_production

    else:
        print("La hora actual no está dentro del rango permitido.")
        return 0
