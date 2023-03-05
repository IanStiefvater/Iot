from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db import connection
from django.utils import timezone

from django.utils import timezone

timezone.activate('America/Argentina/Buenos_Aires')


def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('../../admin')  # redirigir a la proxima pagina
        else:
            messages.success(
                request, ("Credenciales incorrectas"))
            return redirect('login')
    else:  # sino esta logueado redirija a la pagina
        return render(request, 'login/login.html', {})


def start_shift(request):
    if request.method == "POST":
        username = request.POST.get("username")
        shift = request.POST.get("turno")
        line = request.POST.getlist("lines[]")
        if shift is not None and line:
            # print(shift, line)
            with connection.cursor() as cursor:
                for lines in line:
                    cursor.execute(
                        "INSERT INTO linemanagement_line_status (lineName, shift,userId_id,starTime) VALUES (%s, %s,%s,%s)", (lines, shift, 3, timezone.now()))

        else:

            # Handle missing keys
            pass
        redirect("shift")

    name = "Ian"
    num_lines = 3
    return render(request, "login/turno.html", {"name": name, "num_lines": num_lines})
