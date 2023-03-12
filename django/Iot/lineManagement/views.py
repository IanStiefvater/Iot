from datetime import date
from django.shortcuts import render
from login.models import user as loginUser
from .models import config, lines, devices as odevice, device_maintance, line_status
import jinja2


def control(request):
   

    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lineas = request.session.get('lines')
    nameLines = request.session.get('namelines', [])

    results = lines.objects.all()

    status ={}

    for a in nameLines:
         print(a)
         lineprueba= line_status.objects.filter(lineName=a ).first()
         print("xd",lineprueba.status)
         status[a]= lineprueba.status
     
    print(status)
    
    
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
    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lineas": lineas, "namelines": nameLines, "devices": devices, "nameDevices": device_names})


def maintenance(request):
    notes= device_maintance.objects.filter( starTime=date.today())
    print(notes)
    print(date.today)

    return render(request, "lineManagement/maintenance.html", {})
