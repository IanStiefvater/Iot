from datetime import date
from django.contrib.auth import logout

from django.utils import timezone

from django.shortcuts import render, redirect

from .models import user as loginUser
from .models import device_maintance
from .models import lines_maintance
from datetime import date, datetime
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

from login.models import user as loginUser
from .models import config, lines, devices as odevice, device_maintance, line_status as lstatus, device_status as dstatus
from django.db.models import Q
from django.db import models


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
            print(devices_query)
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

    device_names = {}

    # Obtener los dispositivos de las líneas seleccionadas
    devices_query = odevice.objects.filter(line__in=nameLines)
    # Crear un diccionario para almacenar los nombres de los dispositivos en esta línea
    device_names = {}

    # Filtrar los dispositivos por línea y almacenar sus nombres e ids en el diccionario
    for line in nameLines:
        device_names[line] = {}
        # Obtener el estado de cada devices de las lineas
        for device in devices_query.filter(line=line):
            device_status = dstatus.objects.filter(
                deviceId=device).order_by('-starTime').first()
            if device_status:
                device_info = device.name
                device_estado = device_status.status

            else:
                device_info = device.name

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
                "id": device.id, "name": device_info, "status": device_estado, "items": items}
        print(device_names)
        # crear una variable intermedia para acceder a los elementos de `device_names[line]`
        device_items = device_names.get(line, {}).items()

        # Obtener el estado de todos los devices y asignar el estado a la línea
        line_status = {}
        for a in nameLines:
            # Establecer línea como activa por defecto
            line_status[a] = 'activo'
            for device in device_names.get(line, {}).values():
                # Si al menos un dispositivo está activo o en espera, la línea está activa
                if device['status'] != 'inactivo':
                    line_status[a] = 'Activa'
                    break
            else:  # Si no se encontró ningún dispositivo activo o en espera, establecer la línea como inactiva
                line_status[a] = 'inactiva'
        print(line_status[a])

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

    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lineas": lineas, "namelines": nameLines, "devices": devices, "device_items": device_items, "status": line_status})


def maintenance(request):
    line = request.GET.get('line')
    print(line)
    device_name = request.GET.get('device_name')

    print(device_name)
    username = request.GET.get('username')
    shift = request.GET.get('shift')
    line_status = lstatus.objects.filter(
        lineName=line, endTime__isnull=True).first().status
    print("Line Status:", line_status)

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
    print("Line ID:", line_id)
    print("Device ID:", device_id)
    print('Device status:', device_status)

    # los id que obtiene arriba son objetos, aquí abajo se transforman en int para enviarlos a las tablas
    lineId = request.POST.get('line_id')

    if request.method == "POST":
        action = request.POST['action']
        request.session['action'] = action

        if action == 'DETENER':
            option = request.POST.get('options', None)
            notas = request.POST.get('notas', '').strip()
            print("notas: ", notas)

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
    print(notes)
    return render(request, "lineManagement/maintenance.html", {'notes': notes, 'device_name': device_name, 'line': line, 'username': username, 'shift': shift, 'device_status': device_status, 'line_id': line_id, 'device_id': device_id})


def error_404_view(request, exception):
    return render(request, 'error.html', {})
