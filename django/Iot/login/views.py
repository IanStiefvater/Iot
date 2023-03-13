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
from lineManagement.models import config, lines
from lineManagement.models import device_maintance, line_status
from django.contrib.auth.hashers import make_password


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
            return redirect("shift")

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
        line = request.POST.getlist("lines[]")
        if shift is not None and line:

            # print(shift, line)
            with connection.cursor() as cursor:
                linea = []
                for line in line:

                    d = lines.objects.get(name=line)
                    userid = loginUser.objects.filter(
                        iduser=request.session.get('userid')).first()
                    linea.append(d.name)
                    insertarline = line_status(lineName=line, shift=shift, starTime=timezone.now(
                    ), amountDevices=d.amountDevice, userId=userid)
                    insertarline.save()

            request.session['namelines'] = linea
        else:

            # Handle missing keys
            pass
        # aca rederigimos a los del ian
        return redirect("../../linemanagement/home")

    iduser = request.session.get('userid')

    responsable = loginUser.objects.filter(iduser=iduser).first()

    name = responsable.name

    num_lines = config.objects.get(id=1).numLines
    request.session['lines'] = num_lines
    return render(request, "login/turno.html", {"name": name, "num_lines": num_lines})
