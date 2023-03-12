from django.shortcuts import render
from .models import user as loginUser
from .models import device_maintance
from datetime import date, timezone
from django.http import HttpResponse    
from .models import lines_maintance, device_maintance

from .models import config, lines, devices as odevice



def control(request):
    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lineas = request.session.get('lines')
    nameLines = request.session.get('namelines', [])

    results = lines.objects.all()

    devices = {}

    for line in results:
        devices[line.name] = line.amountDevice

    device_names = {}
    for line in set(device.line for device in odevice.objects.all()):

        device_names[line] = {}
        for device in odevice.objects.filter(line=line):
            device_names[line][device.name] = device.id
    print("------")
    print(device_names)
    print("------")
    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lineas": lineas, "namelines": nameLines, "devices": devices, "nameDevices": device_names})


def maintenance(request):
    if request.method == "POST":
        option = request.POST['options']
        notas = request.POST['notas']   
        lineproduction = request.POST['lineproduction'] 
        blocks = request.POST['blocks']
        lines = lines_maintance(deviceid= 1, point= option, notes= notas, starTime= timezone.now())
        lines.save()

    

    notes = device_maintance.objects.all()
    return render(request, "lineManagement/maintenance.html", {'notes': notes})

