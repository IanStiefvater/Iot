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
from .models import config, lines, devices as odevice, device_maintance, line_status
from django.db.models import Q


def control(request):
    nameLines = request.session.get('namelines', [])

    if request.method == "POST":
        if request.POST.get("turno") is not None:
            turno = request.POST.get("turno")
            for a in nameLines:

                lineprueba = line_status.objects.filter(
                    ~Q(status="inactivo"), lineName=a, endTime__isnull=True).first()
                lineprueba.status = "inactivo"
                lineprueba.endTime = timezone.now()
                lineprueba.save()
            logout(request)
            return redirect('login')

    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lineas = request.session.get('lines')

    results = lines.objects.all()

    status = {}

    for a in nameLines:
        print(a)
        lineprueba = line_status.objects.filter(
            ~Q(status="inactivo"), lineName=a, endTime__isnull=True).first()
        print("xd", lineprueba.status)
        status[a] = lineprueba.status

    print(status, "status")

    devices = {}

    for line in results:
        devices[line.name] = line.amountDevice

    device_names = {}


# Obtener las líneas únicas de la base de datos de dispositivos
    for line in set(device.line for device in odevice.objects.all()):

        # Crear un diccionario para almacenar los nombres de los dispositivos en esta línea
        device_names[line] = {}

    # Filtrar los dispositivos por línea y almacenar sus nombres e ids en el diccionario

        for device in odevice.objects.filter(line=line):
            device_names[line][device.deviceId] = device.name

    print(device_names)
    print("------")
    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lineas": lineas, "namelines": nameLines, "devices": devices, "nameDevices": device_names, "status": status})


def maintenance(request):
    line = request.GET.get('line')
    device_name = request.GET.get('device_name')
    username = request.GET.get('username')
    shift = request.GET.get('shift')
    line_status = request.GET.get('line_status')
    
    # Encuentra el objeto de línea y dispositivo que corresponden a la línea y el nombre del dispositivo
    line_object = lines.objects.filter(name=line).first()
    device_object = odevice.objects.filter(name=device_name).first()

    # Obtén los IDs
    line_id = line_object.id
    device_id = device_object.deviceId
    print("Line Object:", line_object)
    print("Device Object:", device_object)
    print("Line ID:", line_id)
    print("Device ID:", device_id)

    #datos que se envían en el formulario
    lineId = request.GET.get('line_id')
    deviceId = request.GET.get('device_id')

    if request.method == "POST":
        action = request.POST['action']
        request.session['action'] = action

        if action == 'DETENCIÓN' and line_status == 'activo':
            option = request.POST.get('options', None)
            notas = request.POST.get('notas', '').strip()

            if option is None or notas == '':
                messages.error(request, 'Por favor, complete todos los campos antes de seleccionar DETENCIÓN.')
                return redirect('maintenance')
            #Captura el momento exacto en donde se envía el formulario (horas, minutos, segundos)
            start_time = datetime.now().strftime("%H:%M:%S")

            lines_maintenance_obj = lines_maintance(lineId=lineId, point=option, notes=notas, starTime=start_time)
            lines_maintenance_obj.save()
            request.session['lines_maintenance_id'] = lines_maintenance_obj.id

            device = device_maintance(deviceId=deviceId, point=option, lineid=line_id, notes=notas, starTime=start_time)
            device.save()
            #request.session sirve para almacenar y recuperar datos específicos del usuario durante múltiples solicitudes (requests)
            request.session['device_maintenance_id'] = device.id

        elif action == 'ARRANQUE':
            # El arranque solo envía el endTime a las tablas, para eso recupera su id que se extranjo de request.session y rellena esa columna vacía que se envía al principío en detención
            end_time = datetime.now().strftime("%H:%M:%S")
            lines_maintenance_id = request.session.get('lines_maintenance_id')
            if lines_maintenance_id:
                lines_maintenance_obj2 = lines_maintance.objects.filter(id=lines_maintenance_id).first()
                if lines_maintenance_obj2:
                    lines_maintenance_obj2.endTime = end_time
                    lines_maintenance_obj2.save()
                    del request.session['lines_maintenance_id']

            device_maintenance_id = request.session.get('device_maintenance_id')
            if device_maintenance_id:
                device_maintenance_obj2 = device_maintance.objects.filter(id=device_maintenance_id).first()
                if device_maintenance_obj2:
                    device_maintenance_obj2.endTime = end_time
                    device_maintenance_obj2.save()
                    del request.session['device_maintenance_id']

    notes = device_maintance.objects.all()
    return render(request, "lineManagement/maintenance.html", {'notes': notes, 'device_name': device_name, 'line': line, 'username': username, 'shift': shift, 'line_status': line_status, 'line_id': line_id, 'device_id': device_id})
