import datetime
from datetime import date
from django.contrib.auth import logout
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import user as loginUser
from .models import device_maintance
from .models import lines_maintance
from datetime import date, datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from login.models import user as loginUser
from .models import config, lines, devices as odevice, device_maintance, line_status as lstatus, device_status as dstatus, device_production as dev_prod, graphs, total_maintenance as totalM
from django.db.models import Q, Count, Sum, Max, F
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from django.db.models.functions import Cast
from django.db.models import DateField
from django.db.models.fields import DurationField
from django.db import models
import paho.mqtt.client as mqtt
import json


def select (request):
    return render (request, 'lineManagement/select.html')

def control(request):
    nameLines = request.session.get('namelines', [])

    if request.method == "POST":
        if request.POST.get("turno") is not None:
            turno = request.POST.get("turno")
            for a in nameLines:

                lineprueba = lstatus.objects.filter(
                    ~Q(status="Terminado"), lineName=a, endTime__isnull=True).first()
                lineprueba.status = "Terminado"
                lineprueba.endTime = timezone.now()
                lineprueba.save()

            devices_query = odevice.objects.filter(line=a)
            # print(devices_query)
            for device in devices_query:
                device_status = dstatus.objects.filter(
                    ~Q(status="Terminado"), deviceId=device.id, endTime__isnull=True).first()
                device_status.status = 'Terminado'
                device_status.endTime = timezone.now()
                device_status.save()
                # Obtener el objeto dev_maintenance
                dev_maintenance = device_maintance.objects.filter(
                    deviceId=device.id, endTime__isnull=True).first()

                # Verificar si dev_maintenance tiene un valor antes de actualizarlo
                if dev_maintenance:
                    dev_maintenance.endTime = timezone.now()
                    dev_maintenance.save()
                    
            """
            if dev_prod.objects.exists():
                # Realizar los cálculos de producción total y capacidad máxima
                line_results = dev_prod.objects.values("deviceId_id", "deviceId__name").annotate(
                    total_production=Sum("production_data"),
                    max_production=Max("production_data"),
                    periods_count=Count("deviceId_id"),
                ).order_by("deviceId_id")

                for result in line_results:
                    device_instance = odevice.objects.get(id=result["deviceId_id"])

                    device_production_data = dev_prod.objects.filter(deviceId_id=result["deviceId_id"]).first()

                    graphs.objects.create(
                        deviceId=device_instance,
                        shift=device_production_data.shift,
                        lineid=device_production_data.lineid,
                        total_production=result["total_production"],
                        potential_production=result["max_production"] * result["periods_count"],
                        date=device_production_data.date,
                        name=result["deviceId__name"],
                    )"""
                    # Borrar todos los datos de la tabla device_production
                    # dev_prod.objects.all().delete()
        
            if device_maintance.objects.exists():
                maintenance_results = device_maintance.objects.values("deviceId", "point", "lineid", "shift", 
                                                                    date_start=Cast('starTime', DateField()),
                                                                    date_end=Cast('endTime', DateField())
                                                                    ).annotate(
                    total_time=Sum(F('endTime') - F('starTime')),
                ).order_by("deviceId", "point")

                for result in maintenance_results:
                    # Convertir timedelta a segundos
                    total_seconds = result["total_time"].total_seconds()

                    # Formatear la fecha de inicio y fin como cadena
                    date_start = result['date_start'].strftime('%Y-%m-%d')


                    totalM.objects.create(
                        deviceId=result["deviceId"],
                        point=result["point"],
                        lineid=result["lineid"],
                        shift=result["shift"],
                        totalTime=total_seconds,
                        date=date_start,
                    )
                     # Borrar todos los datos de la tabla device_maintance
                    # device_maintance.objects.all().delete()"""
        logout(request)
        return HttpResponseRedirect('./select')
       

    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lineas = request.session.get('lines')

    results = lines.objects.all()

    devices = {}

    for line in results:
        devices[line.name] = line.amountDevice

    # print(devices)

    device_names = {}

    # Obtener los dispositivos de las líneas seleccionadas
    devices_query = odevice.objects.filter(line__in=nameLines)
    # Crear un diccionario para almacenar los nombres de los dispositivos en esta línea
    device_names = {}
    #print(nameLines)
    device_items = []
    # Filtrar los dispositivos por línea y almacenar sus nombres e ids en el diccionario
    for line in nameLines:
        device_names[line] = {}
        lineaid = lines.objects.filter(name=line).first()
        # Obtener el estado de cada devices de las lineas
        for device in devices_query.filter(line=line):
            device_status = dstatus.objects.filter(
                deviceId=device, lineid=lineaid.id).order_by('-id').first()  # device id  ordenar por fecha de inicio
            if device_status:
                device_info = device.name
                device_estado = device_status.status
                print(f"{device_info} cuyo id es {device.id}")

            items = []
            if device_status and device_status.status == "activo":
                items.append(
                    {"status": "activo", "css": "background-color: #077a16bf; color: #FFFFFF"})
            elif device_status and device_status.status == "inactivo":
                items.append(
                    {"status": "inactivo", "css": "background-color: red; color: #FFFFFF"})
            elif device_status and device_status.status == "En espera":
                items.append(
                    {"status": "En espera", "css": "background-color: #C9C8BA; color: #737373"})

            device_names[line][device.id] = {
                "id": device.id, "name": device_info, "status": device_estado, "items": items, "line": line, "deviceId": device.id, "lineId": lineaid.id}
        # crear una variable intermedia para acceder a los elementos de `device_names[line]`
        device_items += device_names.get(line, {}).items()

    # print('items:', device_items)

    # Obtener el estado de todos los devices y asignar el estado a la línea
    line_status = {}
    for a in nameLines:
        lineaid = lines.objects.filter(name=a).first()
        line_active = False
        # print(dstatus.objects.filter(lineid=lineaid.id).values())
        # Establecer línea como activa por defecto
        for device in dstatus.objects.filter(lineid=lineaid.id).values():
            # Si al menos un dispositivo está activo o en espera, la línea está activa
            #print(device['status'])
            if device['status'] == 'activo':
                line_active = True
                break

        line_status[a] = 'Activa' if line_active else 'Inactiva'
    print(line_status)

    for line, status in line_status.items():
        line_object = lines.objects.get(name=line)
        line_status_object = lstatus.objects.filter(
            lineName=line, endTime__isnull=True).first()
        if line_status_object:
            line_status_object.status = status
            line_status_object.save()
        else:
            lstatus.objects.create(
                lineName=line_object, status=status, starTime=timezone.now())
    """
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
    # Crear un parámetro de medición que opere en la tabla temporal para determinar si está recibiendo datos o nó en un período de tiempo de 320 segundos
    device_warnings = {}

    for device in devices_query:
            last_dev_prod_entry = dev_prod.objects.filter(deviceId=device.id).first()

            if last_dev_prod_entry:
                last_production_data_time_str = last_dev_prod_entry.created_at.split(',')[-1]
                last_production_data_time = datetime.strptime(last_production_data_time_str, '%Y-%m-%d %H:%M:%S').time()
                current_time = timezone.now().time()
                time_difference = datetime.combine(date.min, current_time) - datetime.combine(date.min, last_production_data_time)
                total_seconds_difference = time_difference.total_seconds()

                if total_seconds_difference > 320.0:
                    device_warnings[device.id] = "Sin envío de datos"


    return render(request, "lineManagement/control.html", {'turno': turno, 
                                                           "name": name, "lineas": lineas, 
                                                           "namelines": nameLines, 
                                                           "devices": devices, 
                                                           "device_items": device_items, 
                                                           "device_names": device_names, 
                                                           "status": line_status, 
                                                           "device_warnings": json.dumps(device_warnings), })
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
    line = request.GET.get('line')
   # print(line)
    device_name = request.GET.get('device_name')

    # print(device_name)
    username = request.GET.get('username')
    shift = request.GET.get('shift')
    line_status = lstatus.objects.filter(
        lineName=line, endTime__isnull=True).first().status
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
    device_id = request.GET.get('deviceID')
    device_status = dstatus.objects.filter(
        deviceId_id=device_id, endTime__isnull=True).first().status
    # print("Line ID:", line_id)
    # print("Device ID:", device_id)
    # print('Device status:', device_status)

    # los id que obtiene arriba son objetos, aquí abajo se transforman en int para enviarlos a las tablas
    lineId = request.POST.get('line_id')

    if request.method == "POST":
        action = request.POST['action']
        request.session['action'] = action

        if action == 'DETENER':
            option = request.POST.get('options', None)
            notas = request.POST.get('notas', '').strip()
            # print("notas: ", notas)

            if option is None or notas == '':
                messages.error(
                    request, 'Por favor, complete todos los campos antes de seleccionar DETENCIÓN.')
                return redirect('maintenance')
            # Captura el momento exacto en donde se envía el formulario (horas, minutos, segundos)

            device = device_maintance(
                deviceId=device_id, point=option, lineid=lineId, notes=notas, shift=shift, starTime=timezone.now())
            device.save()
            status_device = dstatus.objects.filter(
                deviceId_id=device_id, endTime__isnull=True).first()
            status_device.status = "inactivo"
            status_device.save()
            # request.session sirve para almacenar y recuperar datos específicos del usuario durante múltiples solicitudes (requests)
            request.session['device_maintenance_id'] = device.id
            return HttpResponseRedirect('./home')

        elif action == 'ARRANCAR':
            # El arranque solo envía el endTime a las tablas, para eso recupera su id que se extranjo de request.session y rellena esa columna vacía que se envía al principío en detención
            end_time = timezone.now()
            status_device = dstatus.objects.filter(
                deviceId_id=device_id, endTime__isnull=True).first()
            # Rellenar con el endTime la tabla de mantenimiento de dsipositivos
            device_maintenance_id = request.session.get(
                'device_maintenance_id')
            status_device = dstatus.objects.filter(
                deviceId_id=device_id, endTime__isnull=True).first()
            status_device.status = "activo"
            status_device.save()
            if device_maintenance_id:
                device_maintenance_obj2 = device_maintance.objects.filter(
                    id=device_maintenance_id).first()
                if device_maintenance_obj2:
                    device_maintenance_obj2.endTime = end_time
                    device_maintenance_obj2.save()
                    del request.session['device_maintenance_id']
            return HttpResponseRedirect('./home')

    Nota = device_maintance.objects.filter(deviceId=device_id)
    # Crear una lista vacía para almacenar las notas
    notes = []

    # Iterar sobre el queryset y agregar las notas a la lista
    for nota in Nota:
        notes.append(nota)

    # Imprimir la lista de notas
   # print(notes)
    return render(request, "lineManagement/maintenance.html", {'notes': notes, 'device_name': device_name, 'line': line, 'username': username, 'shift': shift, 'device_status': device_status, 'line_id': line_id, 'device_id': device_id})


def error_404_view(request, exception):
    return render(request, 'error.html', {})



def rollover_shifts_and_maintenance():
    midnight_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    midnight_tomorrow = midnight_today + timedelta(days=1)

    # Rollover device_status shifts
    active_device_statuses = dstatus.objects.filter(Q(endTime__isnull=True) | Q(endTime__gt=midnight_tomorrow)).exclude(status='Terminado')
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
            status=active_status.status
        )

    # Rollover line_status shifts
    active_line_statuses = lstatus.objects.filter(Q(endTime__isnull=True) | Q(endTime__gt=midnight_tomorrow)).exclude(status='Terminado')
    for active_status in active_line_statuses:
        # End the current shift
        active_status.endTime = midnight_today
        active_status.save()
        
        # Start a new shift
        lstatus.objects.create(
            lineName=active_status.lineName,
            amountDevices=active_status.amountDevices,
            shift=active_status.shift,
            userId=active_status.userId,
            starTime=midnight_tomorrow,
            status=active_status.status,
            notes=active_status.notes
        )

    # Rollover device_maintenance tasks
    active_maintenance_tasks = device_maintance.objects.filter(Q(endTime__isnull=True) | Q(endTime__gt=midnight_tomorrow))
    for active_task in active_maintenance_tasks:
        # End the current task
        active_task.endTime = midnight_today
        active_task.save()
        
        # Start a new task
        device_maintance.objects.create(
            deviceId=active_task.deviceId,
            point=active_task.point,
            lineid=active_task.lineid,
            notes=active_task.notes,
            shift=active_task.shift,
            starTime=midnight_tomorrow
        )