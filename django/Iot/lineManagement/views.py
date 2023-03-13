from datetime import date

from django.utils import timezone

from django.shortcuts import render
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
    notes = device_maintance.objects.filter(starTime=date.today())
    print(notes)
    print(date.today)

    return render(request, "lineManagement/maintenance.html", {})
