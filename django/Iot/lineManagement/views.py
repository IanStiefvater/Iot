from django.shortcuts import render
from .models import user as loginUser
from .models import device_maintance
from datetime import date, timezone
from django.http import HttpResponse    
from .models import lines_maintance, device_maintance


def control(request):
    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lines = request.session.get('lines')

    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lines": lines})


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

