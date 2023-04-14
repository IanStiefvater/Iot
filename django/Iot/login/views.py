from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.contrib.auth.decorators import login_required

from .models import user as loginUser
from lineManagement.models import lines, devices
from lineManagement.models import device_maintance, line_status, device_status
from django.contrib.auth.hashers import make_password
import paho.mqtt.client as mqtt
 
from django.utils import timezone

timezone.activate('America/Argentina/Buenos_Aires')


def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        print(password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session["userid"] = user.id
            u = loginUser(name=user.username, email=user.email, iduser=user.id)
            u.save()

            # redirigir a la proxima pagina
            return HttpResponseRedirect('/authenticate/shift/')

        else:
            messages.success(
                request, ("Credenciales incorrectas"))
            return redirect('login')
    else:  # sino esta logueado redirija a la pagina
        return render(request, 'login/login.html', {})




@login_required
def start_shift(request):
    if request.method == "POST":
        username = request.POST.get("username")
        shift = request.POST.get("turno")
        request.session['turno'] = shift
        # Se obtienen todas las líneas seleccionadas
        selected_lines = request.POST.getlist("lines[]")

        if shift is not None and selected_lines:
            lines_ids = []
            linea = []
            for line in selected_lines:
                # Obtener información de la línea
                line_obj = lines.objects.get(name=line)
                lines_ids.append(line_obj.id)
                linea.append(line_obj.name)
                print('nombre de la linea : ', linea)
                print('id de la línea : ', line_obj.id)
                # Insertar línea en tabla line_status
                user_obj = loginUser.objects.filter(
                    iduser=request.session.get('userid')).first()
                insertarline = line_status(lineName=line_obj.name, shift=shift, starTime=timezone.now(),
                                           amountDevices=line_obj.amountDevice, status="activa", userId=user_obj)
                insertarline.save()
                # Obtener dispositivos de la línea
                devices_query = devices.objects.filter(line=line_obj.name)
                device_ids = devices_query.values_list('id', flat=True)
                devices_names = devices_query.values_list('name', flat=True)
                print(devices_query)
                print(devices_names)
                print(device_ids)

                for device_id in device_ids:
                    device_obj = devices.objects.get(id=device_id)
                    insertar_device_status = device_status(
                        deviceId=device_obj, shift=shift, starTime=timezone.now(), lineid=line_obj.id, data=0)
                    insertar_device_status.save()

            request.session['namelines'] = linea

        else:
            # Handle missing keys
            pass

        # Redireccionar a los del ian
        return redirect("../../linemanagement/home")

    iduser = request.session.get('userid')
    responsable = loginUser.objects.filter(iduser=iduser).first()
    name = responsable.name

    lineas = list(lines.objects.all().values('name'))
    request.session['lineas'] = lineas
    return render(request, "login/turno.html", {"name": name, "lineas": lineas})


def error_404_view(request, exception):
    return render(request, 'error.html', {})

