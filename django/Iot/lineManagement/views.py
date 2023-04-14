from datetime import date
from django.contrib.auth import logout

from django.utils import timezone

from django.shortcuts import render, redirect

from .models import user as loginUser
from .models import device_maintance
from .models import lines_maintance
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

from login.models import user as loginUser
from .models import config, lines, devices as odevice, device_maintance, line_status as lstatus, device_status as dstatus, device_production as dev_prod
from django.db.models import Q
from django.db import models
import paho.mqtt.client as mqtt
import json



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
                dev_maintenance = device_maintance.objects.filter(
                    deviceId=device.id, endTime__isnull=True).first()
                dev_maintenance.endTime = timezone.now()
                dev_maintenance.save()
            logout(request)
            return redirect('login')

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
               # print(f"{device_info} cuyo id es {device.id}")

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
    reload_page = False
    # Crear un parámetro de medición que opere en la tabla temporal para determinar si está recibiendo datos o nó en un período de tiempo de 320 segundos
    device_warnings = {}

    for device in devices_query:
            last_dev_prod_entry = dev_prod.objects.filter(deviceId=device.id).first()

            if last_dev_prod_entry:
                last_production_data_time_str = last_dev_prod_entry.created_at.split(',')[-1]
                last_production_data_time = datetime.strptime(last_production_data_time_str, '%H:%M:%S').time()
                current_time = timezone.now().time()
                time_difference = datetime.combine(date.min, current_time) - datetime.combine(date.min, last_production_data_time)
                total_seconds_difference = time_difference.total_seconds()

                if total_seconds_difference> timedelta(seconds=320):
                    device_warnings[device.id] = "Sin envío de datos"
                    reload_page = True #Cuando el condicional se cumple, se envía una señal al cliente para recargar la página y así que aparezca la advertencia

    return render(request, "lineManagement/control.html", {'turno': turno, 
                                                           "name": name, "lineas": lineas, 
                                                           "namelines": nameLines, 
                                                           "devices": devices, 
                                                           "device_items": device_items, 
                                                           "device_names": device_names, 
                                                           "status": line_status, 
                                                           "device_warnings": device_warnings, 
                                                           "reload_page": reload_page})
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

    # Buscar si ya existe una entrada en la tabla para este dispositivo y turno
    dev_prod_entry = dev_prod.objects.filter(deviceId=device_id, shift=shift).first()

    # Si no existe una entrada, crear una nueva
    if dev_prod_entry is None:
        device_instance = dstatus.objects.get(id=device_id)
        dev_prod_entry = dev_prod(deviceId=device_instance, lineid=line_id, shift=shift, production_data=str(production_data),created_at=timezone.now().strftime('%H:%M:%S' ), date=timezone.now().date())
        dev_prod_entry.set_date_from_status()
        dev_prod_entry.save()
    else:
        # Si existe una entrada, agregar los nuevos datos de producción separados por comas
        dev_prod_entry.production_data += f", {production_data}"
        dev_prod_entry.created_at += f",{timezone.now().strftime('%H:%M:%S')}" #agrega el snapshot preciso en el que ingresó el dato de producción
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
                deviceId=device_id, point=option, lineid=lineId, notes=notas, starTime=timezone.now())
            device.save()
            status_device = dstatus.objects.filter(
                deviceId_id=device_id, endTime__isnull=True).first()
            status_device.status = "inactivo"
            status_device.save()
            # request.session sirve para almacenar y recuperar datos específicos del usuario durante múltiples solicitudes (requests)
            request.session['device_maintenance_id'] = device.id
            return redirect('home')

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
            return redirect('home')

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
