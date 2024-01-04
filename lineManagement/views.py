import datetime
from datetime import date
from django.contrib.auth import logout
from django.utils import timezone
from django.db import connection
from dateutil import tz
from django.shortcuts import render, redirect
from lineManagement.controllers.device_details.details import get_ph, shift_production
from lineManagement.controllers.device_details.graph import dataGraph
from .models import usuarios as loginUser, config_shift
from login.models import log_users
from .models import device_maintenance, supervisor
from .models import lines_maintenance, device_production
from datetime import date, datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from login.models import usuarios as loginUser
import pytz
from .models import (
    config,
    lines,
    devices as odevice,
    device_maintenance,
    line_status as lstatus,
    device_status as dstatus,
    device_production as dev_prod,
    total_maintenance as totalM,
)
from django.db.models import Q, Count, Sum, Max, F, Avg
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from django.db.models.functions import Cast
from django.db.models import DateField
from django.db.models.fields import DurationField
from django.db import models
import paho.mqtt.client as mqtt
from django.shortcuts import get_object_or_404
import json


def select(request):
    return render(request, "lineManagement/select.html")


def control(request):
    lineadict = list(lines.objects.all().values_list("name", flat=True))
    if request.method == "POST":
        if request.POST.get("turno") is not None:
            turno = request.POST.get("turno")
            for a in lineadict:
                try:
                    lineprueba = lstatus.objects.filter(
                        ~Q(status="Terminado"), lineName=a, endTime__isnull=True
                    ).first()
                    lineprueba.status = "Terminado"
                    lineprueba.endTime = timezone.now()
                    lineprueba.save()
                except AttributeError as e:
                    print(f"Ocurrió un error al procesar la línea {a}: {str(e)}")
                    print(f"Valor de lineprueba: {lineprueba}")

                # Mover la operación de los dispositivos dentro del bucle de las líneas
                line_ids = lines.objects.filter(name=a).values_list("id", flat=True)
                for line_id in line_ids:
                    print(line_id)

                    devices_status_query = dstatus.objects.filter(
                        lineid=line_id
                    ).exclude(status="Terminado")

                    # Obtener los devices_ids antes de actualizar el status
                    devices_ids = devices_status_query.values_list(
                        "deviceId", flat=True
                    )
                    print(f"Devices IDs: {devices_ids}")

                    for device_status in devices_status_query:
                        device_status.status = "Terminado"
                        device_status.endTime = timezone.now()
                        device_status.save()

                try:
                    maintenances = device_maintenance.objects.filter(
                        endTime__isnull=True
                    )
                    for maintenance in maintenances:
                        maintenance.endTime = timezone.now()
                        maintenance.save()
                except Exception as e:
                    print(f"Error updating maintenance: {str(e)}")

            # Borrar todos los datos de la tabla device_production
            # dev_prod.objects.all().delete()
            if device_maintenance.objects.exists():
                maintenance_results = (
                    device_maintenance.objects.values(
                        "deviceId",
                        "point",
                        "lineid",
                        "shift",
                        date_start=Cast("starTime", DateField()),
                        date_end=Cast("endTime", DateField()),
                    )
                    .annotate(
                        total_time=Sum(F("endTime") - F("starTime")),
                    )
                    .order_by("deviceId", "point")
                )

                for result in maintenance_results:
                    # Convertir timedelta a segundos
                    total_seconds = result["total_time"].total_seconds()

                    # Formatear la fecha de inicio y fin como cadena
                    date_start = result["date_start"].strftime("%Y-%m-%d")

                    totalM.objects.create(
                        deviceId=result["deviceId"],
                        point=result["point"],
                        lineid=result["lineid"],
                        shift=result["shift"],
                        totalTime=total_seconds,
                        date=date_start,
                    )
                    # Borrar todos los datos de la tabla device_maintenance
                    # device_maintenance.objects.all().delete()"""
        logout(request)
        exit_log = log_users.objects.filter(exit__isnull=True).order_by("-id").first()
        argentina_tz = pytz.timezone("America/Argentina/Buenos_Aires")

        # Obtiene la hora y fecha actual en Argentina
        fecha_actual_argentina = datetime.now(argentina_tz)

        # Formatea la fecha actual en Argentina (Año-Mes-Día)
        fecha_formateada = fecha_actual_argentina.strftime("%Y-%m-%d %H:%M")
        exit_log.exit = fecha_formateada
        exit_log.save()
        return HttpResponseRedirect("./select")

    lineadict = list(lines.objects.all().values_list("name", flat=True))
    # nameLines = lineadict

    turno = request.session.get("turno")
    iduser = request.session.get("userid")
    responsable = loginUser.objects.filter(id=iduser).first()
    print(responsable)
    name = responsable.nombre
    lineas = [line.name for line in lines.objects.all()]

    #   lineas = lines.objects.values_list("name", flat=True)

    results = lines.objects.all()

    devices = {}

    for line in results:
        devices[line.name] = line.amountDevice

    # print(devices)

    device_names = {}

    # Obtener los dispositivos de las líneas seleccionadas
    devices_query = odevice.objects.filter(line__in=lineadict)
    # Crear un diccionario para almacenar los nombres de los dispositivos en esta línea
    device_names = {}
    # print(nameLines)
    device_items = []
    # Filtrar los dispositivos por línea y almacenar sus nombres e ids en el diccionario
    for line in lineadict:
        line_name = line  # Obtener el valor de la clave "name" del diccionario
        device_names[line_name] = {}  # Usar el valor como clave para device_names

        lineaid = lines.objects.filter(name=line).first()
        # Obtener el estado de cada dispositivo de las líneas
        for device in devices_query.filter(line=line):  # Filtrar por línea
            device_status = (
                dstatus.objects.filter(deviceId=device, lineid=lineaid.id)
                .exclude(status="Terminado")
                .order_by("-id")
                .first()
            )

            if device_status:
                device_info = device.name
                device_estado = device_status.status
                print(f"{device_info} cuyo id es {device.id}")

                items = []
                if device_status.status == "activo":
                    items.append(
                        {
                            "status": "activo",
                            "css": "background-color: #077a16bf; color: #FFFFFF",
                        }
                    )
                elif device_status.status == "inactivo":
                    items.append(
                        {
                            "status": "inactivo",
                            "css": "background-color: red; color: #FFFFFF",
                        }
                    )
                elif device_status.status == "En espera":
                    items.append(
                        {
                            "status": "En espera",
                            "css": "background-color: #C9C8BA; color: #737373",
                        }
                    )

                # Agregar el elemento al final de device_items como un diccionario
                device_items.append(
                    {
                        "id": device.id,
                        "name": device_info,
                        "status": device_estado,
                        "items": items,
                        "line": line,
                        "deviceId": device.id,
                        "lineId": lineaid.id,
                    }
                )
    # print('items:', device_items)
    import logging

    # Obtener el estado de todos los devices y asignar el estado a la línea
    line_status = {}
    for a in lineadict:
        lineaid = lines.objects.filter(name=a).first()
        line_active = False
        # print(dstatus.objects.filter(lineid=lineaid.id).values())
        # Establecer línea como activa por defecto
        for device in dstatus.objects.filter(lineid=lineaid.id).values():
            # Si al menos un dispositivo está activo o en espera, la línea está activa
            # print(device['status'])
            if device["status"] == "activo":
                line_active = True
                break

        line_status[a] = "Activa" if line_active else "Inactiva"
    print(line_status)

    """ for line, status in line_status.items():
        line_object = lines.objects.get(name=line)
        line_status_object = lstatus.objects.filter(
            lineName=line_object, endTime__isnull=True
        ).first()
        if line_status_object:
            line_status_object.status = status.status
            line_status_object.save()
        else:
            lstatus.objects.create(
                lineName=line_object,
                status=status,
                starTime=timezone.now(),
                userId_id=iduser,
            )
    """ """
    # Inicializar el cliente MQTT
    mqtt_client = mqtt.Client() #Aquí se utiliza la biblioteca Client() de la librería paho.mqtt.client. Esta crea instancias de clientes MQTT
    mqtt_client.on_message = on_message #Indica que cuando se reciba un mensaje del tópico suscribo, se llame a la función o_message que contiene toda la info del mensaje.

    # Conectar al broker MQTT
    mqtt_client.connect("your_mqtt_broker_address", 1883)

    # Suscribirse a los tópicos de los dispositivos
    for device in devices_query:
        topic = f"deviceId={device.id}"
        mqtt_client.subscribe(topic)
        # Publicar el turno en un tópico relacionado con el dispositivo
        mqtt_client.publish(topic, turno)

    # Iniciar el bucle para recibir mensajes
    mqtt_client.loop_start()"""
    # C""" rear un parámetro de medición que opere en la tabla temporal para determinar si está recibiendo datos o nó en un período de tiempo de 320 segundos
    device_warnings = {}

    for device in devices_query:
        last_dev_prod_entry = dev_prod.objects.filter(deviceId_id=device.id).first()

        if last_dev_prod_entry:
            last_production_data_time_str = last_dev_prod_entry.created_at.split(",")[
                -1
            ].strip()  # Remove leading/trailing spaces
            try:
                last_production_data_time = datetime.strptime(
                    last_production_data_time_str, "%Y-%m-%d %H:%M:%S.%f"
                ).time()
            except ValueError as e:
                # Handle the case where the string format is incorrect
                print(f"Error: {e}")
                continue  # Skip this iteration or add appropriate error handling

    return render(
        request,
        "lineManagement/control.html",
        {
            "turno": turno,
            "name": name,
            "lineas": lineas,
            "namelines": lineadict,
            "devices": devices,
            "device_items": device_items,
            "device_names": device_names,
            "status": line_status,
            "device_warnings": json.dumps(device_warnings),
        },
    )


"""
def on_message(client, userdata, message): #Message es un bjeto que contiene toda la información del mensaje recibido, el tópico, el contenido (payload), etc
 # Extraer el deviceId del tópico
    topic_parts = message.topic.split("=") #divide la cadena en 2 a la altura del símobolo "=", que el formato al cual se suscribe Django: "deviceID={device.id}"
    device_id = int(topic_parts[1]) #toma el segundo valor de esta cadena, es decir {device.id}

    # Decodificar el mensaje JSON
    data = json.loads(message.payload.decode())

    # Extraer los campos del mensaje
    line_id = data["lineId"]
    shift = data["shift"]
    production_data = data["production_data"]

    device_instance = dstatus.objects.get(id=device_id)

    # Buscar el nombre del dispositivo en la tabla devices
    device_name = devices.objects.get(id=device_id).name

    # Crear una nueva entrada en la tabla dev_prod con el nombre del dispositivo
    dev_prod_entry = dev_prod(deviceId=device_instance, name=device_name, lineid=line_id, shift=shift, production_data=str(production_data),created_at=timezone.now().strftime('%H:%M:%S' ), date=timezone.now().date())
    dev_prod_entry.set_date_from_status()
    dev_prod_entry.save()

    print(f"Mensaje recibido: {message.payload.decode()} en el tópico {message.topic}")

def check_and_reset_device_production():
    # Obtener el último estado de device_status y line_status
    last_device_status = dstatus.objects.order_by('-starTime').first()
    last_line_status = lstatus.objects.order_by('-starTime').first()

    # Comprobar si el último estado es "Terminado"
    if (last_device_status and last_device_status.status == "Terminado") or (last_line_status and last_line_status.status == "Terminado"):
        # Si el último estado es "Terminado", eliminar todos los registros en la tabla device_production
        dev_prod.objects.all().delete()"""


def maintenance(request):
    line = request.GET.get("line")
    # print(line)
    device_name = request.GET.get("device_name")

    # print(device_name)
    username = request.GET.get("username")
    shift = request.GET.get("shift")
    line_status = (
        lstatus.objects.filter(lineName=line, endTime__isnull=True).last().status
    )
    # print("Line Status:", line_status)

    # Encuentra el objeto de línea y dispositivo que corresponden a la línea y el nombre del dispositivo
    line_object = lines.objects.filter(name=line).first()
    device_object = odevice.objects.filter(name=device_name).first()

    # Agregar mensajes de depuración
    if line_object is None:
        print("Line object is None")
    if device_object is None:
        print("Device object is None")

    # Obtén los IDs
    line_id = line_object.id
    device_id = request.GET.get("deviceID")
    device_status = (
        dstatus.objects.filter(deviceId_id=device_id)
        .exclude(status="Terminado")
        .first()
        .status
    )

    # print("Line ID:", line_id)
    # print("Device ID:", device_id)
    # print('Device status:', device_status)

    # los id que obtiene arriba son objetos, aquí abajo se transforman en int para enviarlos a las tablas
    lineId = request.POST.get("line_id")

    last_boot = device_maintenance.objects.filter(deviceId=device_id).last().starTime

    if request.method == "POST":
        action = request.POST["action"]
        request.session["action"] = action

        if action == "DETENER":
            option = request.POST.get("options", None)
            notas = request.POST.get("notas", "").strip()
            # print("notas: ", notas)

            sup_prod = request.POST.get("sup_prod")
            if option is None or notas == "":
                messages.error(
                    request,
                    "Por favor, complete todos los campos antes de seleccionar DETENCIÓN.",
                )
                return redirect("maintenance")
            # Captura el momento exacto en donde se envía el formulario (horas, minutos, segundos)
            sup_maintenance = None
            if request.POST.get("sup_maintenance") != None:
                sup_maintenance = request.POST.get("sup_maintenance")

            device = device_maintenance(
                deviceId=device_id,
                point=option,
                lineid=lineId,
                notes=notas,
                shift=shift,
                starTime=timezone.now(),
                maintenanceSupervisor=sup_maintenance,
                productionsupervisor=sup_prod,
            )
            device.save()
            status_device = (
                dstatus.objects.filter(deviceId_id=device_id)
                .exclude(status="Terminado")
                .first()
            )

            status_device.status = "inactivo"
            status_device.save()

            # request.session sirve para almacenar y recuperar datos específicos del usuario durante múltiples solicitudes (requests)
            request.session["device_maintenance_id"] = device.id
            return HttpResponseRedirect("./home")

        elif action == "ARRANCAR":
            # El arranque solo envía el endTime a las tablas, para eso recupera su id que se extranjo de request.session y rellena esa columna vacía que se envía al principío en detención
            end_time = timezone.now()
            status_device = dstatus.objects.filter(deviceId_id=device_id).first()

            # Rellenar con el endTime la tabla de mantenimiento de dsipositivos
            device_maintenance_id = request.session.get("device_maintenance_id")
            status_device = (
                dstatus.objects.filter(deviceId_id=device_id)
                .exclude(status="Terminado")
                .first()
            )
            status_device.status = "activo"

            status_device.save()
            if device_maintenance_id:
                device_maintenance_obj2 = device_maintenance.objects.filter(
                    id=device_maintenance_id
                ).first()
                if device_maintenance_obj2:
                    device_maintenance_obj2.endTime = end_time
                    device_maintenance_obj2.save()
                    del request.session["device_maintenance_id"]
            return HttpResponseRedirect("./home")

    Nota = device_maintenance.objects.filter(deviceId=device_id).order_by("-id")[:10]
    # Crear una lista vacía para almacenar las notas
    notes = []

    # Iterar sobre el queryset y agregar las notas a la lista
    for nota in Nota:
        notes.append(nota)

    registros_filtrados = supervisor.objects.filter(type="Mantenimiento")
    Sup_maintenance_query = registros_filtrados.values_list("name", flat=True)

    # Inicializar una lista vacía
    Sup_maintenance = []

    for nombre in Sup_maintenance_query:
        Sup_maintenance.append(nombre)  # Añadir cada nombre a la lista

    print(Sup_maintenance)

    registros_filtrados = supervisor.objects.filter(type="Produccion")
    Sup_prod_query = registros_filtrados.values_list("name", flat=True)

    # Inicializar una lista vacía
    Sup_prod = []

    for nombre in Sup_prod_query:
        Sup_prod.append(nombre)  # Añadir cada nombre a la lista

    print(Sup_maintenance)

    # Imprimir la lista de notas
    # print(notes)
    return render(
        request,
        "lineManagement/maintenance.html",
        {
            "sup_maintenance": Sup_maintenance,
            "sup_prod": Sup_prod,
            "notes": notes,
            "device_name": device_name,
            "line": line,
            "username": username,
            "shift": shift,
            "device_status": device_status,
            "line_id": line_id,
            "device_id": device_id,
            "last_boot": last_boot,
        },
    )


def error_404_view(request, exception):
    return render(request, "error.html", {})


def rollover_shifts_and_maintenance():
    midnight_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_tomorrow = midnight_today + timedelta(days=1)

    # Rollover device_status shifts
    active_device_statuses = dstatus.objects.exclude(status="Terminado")
    for active_status in active_device_statuses:
        # End the current shift
        active_status.endTime = midnight_today
        active_status.save()

        # Start a new shift
        dstatus.objects.create(
            deviceId=active_status.deviceId,
            shift=active_status.shift,
            data=active_status.data,
            lineid=active_status.lineid,
            starTime=midnight_tomorrow,
            status=active_status.status,
        )

    # Rollover line_status shifts
    iduser = request.session.get("userid")
    active_line_statuses = lstatus.objects.filter(
        Q(endTime__isnull=True) | Q(endTime__gt=midnight_tomorrow)
    ).exclude(status="Terminado")
    for active_status in active_line_statuses:
        # End the current shift
        active_status.endTime = midnight_today
        active_status.save()

        # Start a new shift
        lstatus.objects.create(
            lineName=active_status.lineName,
            amountDevices=active_status.amountDevices,
            shift=active_status.shift,
            userId_id=iduser,
            starTime=midnight_tomorrow,
            status=active_status.status,
            notes=active_status.notes,
        )

    # Rollover device_maintenance tasks
    active_maintenance_tasks = device_maintenance.objects.filter(
        Q(endTime__isnull=True) | Q(endTime__gt=midnight_tomorrow)
    )
    for active_task in active_maintenance_tasks:
        # End the current task
        active_task.endTime = midnight_today
        active_task.save()

        # Start a new task
        device_maintenance.objects.create(
            deviceId=active_task.deviceId,
            point=active_task.point,
            lineid=active_task.lineid,
            notes=active_task.notes,
            shift=active_task.shift,
            starTime=midnight_tomorrow,
        )


def line_detail(request, lineName):
    lineName = lineName[:5] + " " + lineName[5:]
    linesID = lines.objects.get(name=lineName).id

    # Obtener la zona horaria de Argentina/Mendoza
    timezone = pytz.timezone("America/Argentina/Mendoza")

    # Obtener la hora actual en la zona horaria específica
    hora_actual = datetime.now(timezone)

    # Calcular la hora hace una hora atrás
    hora_anterior = hora_actual - timedelta(hours=1)

    # Filtrar las filas para la última hora
    filas_ultima_hora = device_production.objects.filter(
        lineid=linesID,
        created_at__gte=hora_anterior,
        created_at__lte=hora_actual,
    )
    sum_production = filas_ultima_hora.aggregate(Sum("production_data"))[
        "production_data__sum"
    ]
    # Calcular el promedio de las columnas específicas
    promedio_voltage = filas_ultima_hora.aggregate(Avg("battery_voltage"))[
        "battery_voltage__avg"
    ]
    """  promedio_battery_percentage = filas_ultima_hora.aggregate(
        Avg("battery_percentage")
    )["battery_percentage__avg"] """
    promedio_temperature = filas_ultima_hora.aggregate(Avg("temperature"))[
        "temperature__avg"
    ]

    if sum_production is None:
        sum_production = 0

    if promedio_temperature is None or promedio_temperature == "undefined":
        promedio_temperature = "Sin datos"
    data = {
        "produccion": sum_production,
        # "Promedio Battery Percentage": promedio_battery_percentage,
        "Promedio Temperature": promedio_temperature,
    }

    return JsonResponse(data)


def device_detail(request, lineName, deviceid):
    lineName = lineName[:5] + " " + lineName[5:]
    linesID = lines.objects.get(name=lineName).id
    device = (
        device_production.objects.filter(deviceId_id_id=deviceid, lineid=linesID)
        .order_by("-id")
        .first()
    )

    ph = get_ph(deviceid, linesID)

    pt = shift_production(deviceid, linesID)
    if pt is None:
        pt = 0
    lastregistproduction = device_production.objects.filter(
        lineid=linesID, deviceId_id_id=deviceid
    ).last()
    timezone = pytz.timezone("America/Argentina/Mendoza")
    hora_actual = datetime.now(timezone)

    # Convertir la cadena a datetime y agregar la información de zona horaria
    try:
        lastregistproduction_datetime = datetime.strptime(
            lastregistproduction.created_at, "%Y-%m-%d %H:%M:%S.%f"
        )

    except ValueError:
        # Si eso falla, intentar analizar la fecha sin microsegundos
        lastregistproduction_datetime = datetime.strptime(
            lastregistproduction.created_at, "%Y-%m-%d %H:%M:%S"
        )
    lastregistproduction_datetime = timezone.localize(lastregistproduction_datetime)

    if lastregistproduction_datetime + timedelta(hours=8) < hora_actual:
        lastregistproduction.battery_percentage = "Sin datos"
        lastregistproduction.battery_voltage = "Sin datos"
        lastregistproduction.temperature = "Sin datos"
    if lastregistproduction is not None:
        temperature = lastregistproduction.temperature
        # Resto del código para procesar la temperatura

    voltage = lastregistproduction.battery_voltage
    battery_percentage = lastregistproduction.battery_percentage

    # Calcular la hora hace una hora atrás

    data = {
        "prueba": lastregistproduction_datetime,
        "timedelta": (lastregistproduction_datetime + timedelta(hours=8)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "dia actual": hora_actual,
        "PH": ph,
        "Produccion_Total": pt,
        "voltage": voltage,
        "battery_percentage": battery_percentage,
        "temperature": temperature,
        # Otros datos que deseas incluir en la respuesta
    }

    return JsonResponse(data)


def hour_shift(request):
    timezone = tz.gettz("America/Argentina/Mendoza")
    hora_actual = datetime.now(timezone)
    hora_actual_str = hora_actual.strftime("%H:%M:$S")
    turno = config_shift.objects.filter(
        startTime__lte=hora_actual_str, endTime__gte=hora_actual_str
    ).first()
    """   clock = timedelta(
        hours=hora_actual.hour - turno.startTime.hour,
        minutes=hora_actual.minute - turno.startTime.minute,
    )
    clock = clock.strftime("%H:%M") """
    diferencia_minutos = (hora_actual.hour * 60 + hora_actual.minute) - (
        turno.startTime.hour * 60 + turno.startTime.minute
    )

    # Obtener horas y minutos
    horas, minutos = divmod(diferencia_minutos, 60)
    clock = horas = str(horas) + ":" + str(minutos) + ":" + str(hora_actual.second)
    return JsonResponse({"clock": clock})


def graph(request, lineName):
    data = dataGraph(lineName)

    return data
