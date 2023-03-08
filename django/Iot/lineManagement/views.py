from django.shortcuts import render
from .models import user as loginUser


def control(request):
    turno = request.session.get('turno')
    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name
    lines = 1  # request.session.get('lines')
    nameLines = request.session.get('namelines', [])
    print(nameLines)

    return render(request, "lineManagement/control.html", {'turno': turno, "name": name, "lines": lines, "namelines": nameLines})


def maintenance(request):

    return render(request, "lineManagement/maintenance.html", {})
