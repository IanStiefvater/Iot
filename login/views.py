from datetime import date, datetime, timedelta

import logging
import random
import string
from django.urls import reverse
import pdb
import pytz

from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta


import pdb

import pytz


from .models import usuarios as loginUser, delete_notes, log_users
from lineManagement.models import config_shift, lines, devices, supervisor
from lineManagement.models import (
    device_maintenance,
    line_status,
    device_status,
    device_production,
)
import paho.mqtt.client as mqtt
import json

from django.utils import timezone
from django.db.models import F


timezone.activate("America/Argentina/Buenos_Aires")


# views.py


def recover_passwd(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = loginUser.objects.get(email=email)
        except loginUser.DoesNotExist:
            messages.error(request, f"Correo no encontrado: {email}")
            return render(request, "login/recovery_error.html")

        # Generate a random token for the recovery link
        token = "".join(random.choices(string.ascii_letters + string.digits, k=20))

        # Save the token in the user model for recovery use
        user.token = token
        user.save()

        # Send the recovery email
        subject = "Recuperación de contraseña"
        message = f'Haga clic en el siguiente enlace para restablecer su contraseña: {request.build_absolute_uri("/prueba/authenticate/reset-password/")}?token={token}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, f"Correo enviado correctamente a: {email}")
            storage = messages.get_messages(request)
            last_message = None
            for message in storage:
                last_message = str(message)
        except Exception as e:
            messages.error(request, f"Error al enviar el correo: {str(e)}")
            storage = messages.get_messages(request)
            last_message = None
            for message in storage:
                last_message = str(message)

        return render(request, "login/recoverpass.html", {"last_message": last_message})
    return render(request, "login/recoverpass.html")


def reset_password(request):
    token = request.GET.get("token")
    if not token:
        messages.error(request, "Token no proporcionado.")
        storage = messages.get_messages(request)
    last_message = None
    for message in storage:
        last_message = message
        return redirect(
            "login", {last_message: last_message}
        )  # Redirecciona a la página de inicio de sesión o a donde quieras

    try:
        user = loginUser.objects.get(token=token)
    except loginUser.DoesNotExist:
        messages.error(request, "Token inválido o expirado.")
        return redirect(
            "login"
        )  # Redirecciona a la página de inicio de sesión o a donde quieras

    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_new_password = request.POST["confirm_new_password"]
        if new_password == confirm_new_password:
            # Restablecer la contraseña y limpiar el token
            user.password = make_password(new_password)
            user.token = "hadshdahasdh"
            user.save()
            messages.success(
                request,
                "Contraseña restablecida correctamente. Ahora puedes iniciar sesión con tu nueva contraseña.",
            )
            return redirect(
                "login"
            )  # Redirecciona a la página de inicio de sesión o a donde quieras
        else:
            messages.error(request, "Las contraseñas no coinciden.")

    return render(request, "login/reset_password.html", {"token": token})


def login_user(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            user = loginUser.objects.get(email=email)
            argentina_tz = pytz.timezone("America/Argentina/Buenos_Aires")

            # Obtiene la hora y fecha actual en Argentina
            fecha_actual_argentina = datetime.now(argentina_tz)

            # Formatea la fecha actual en Argentina (Año-Mes-Día)
            fecha_formateada = fecha_actual_argentina.strftime("%Y-%m-%d %H:%M")
            log_login = log_users(id_user_id=user.id, entry=fecha_formateada)
            log_login.save()
            request.session["userid"] = user.id

            return redirect("shift")
        else:
            messages.error(request, "Credencias incorrectas")
            logging.error(
                f"Fallo en la autenticación para el correo electrónico: {email}"
            )

    return render(request, "login/login.html")


@login_required
def start_shift(request):
    iduser = request.session.get("userid")
    responsable = loginUser.objects.get(id=iduser)
    name = responsable.nombre
    usertype = responsable.type
    messages.success(request, f"Inicio de sesión correcto para el usuario: {usertype}")
    storage = messages.get_messages(request)
    last_message = None
    for message in storage:
        last_message = message
    print(
        f"el id user es: {iduser}, cuyo responsable es: {responsable}, y su nombre es: {name}"
    )
    if request.method == "POST":
        iduser = request.session.get("userid")
        shift = request.POST.get("turno")
        request.session["turno"] = shift
        lines_ids = []
        linea = []

        # Obtén todas las líneas seleccionadas (esto depende de cómo deseas obtener las líneas)
        lineas = lines.objects.all().values_list("name", flat=True)
        # justa esto según tus necesidades

        timezone = pytz.timezone("America/Argentina/Mendoza")
        hora_actual = datetime.now(timezone)

        for line in lineas:
            dataline = lines.objects.filter(name=line, status="activo").last()
            try:
                shift_now = line_status.objects.filter(lineName=line).last()

                if shift_now.status == "Activa":
                    # return JsonResponse({"lineas": "hola"})
                    time_difference = hora_actual - shift_now.starTime
                    if shift_now.shift == shift and time_difference >= timedelta(
                        hours=1
                    ):
                        shift_now.endTime = hora_actual
                        shift_now.save()
                    # pdb.set_trace()

                else:
                    # return JsonResponse({"lineas": "chau"})
                    # lines_ids.append(line.id)
                    # linea.append(line.name)

                    lineName = line
                    insertarline = line_status(
                        lineName=line,
                        shift=shift,
                        starTime=hora_actual,
                        amountDevices=4,
                        status="Activa",
                        userId_id=iduser,
                    )
                    insertarline.save()

                    # Obtener dispositivos de la línea
                    devices_query = devices.objects.filter(line=line)
                    device_ids = devices_query.filter(line=line).values_list(
                        "id", flat=True
                    )
                    devices_names = devices_query.values_list("name", flat=True)
                    print(devices_query)
                    print(devices_names)
                    print(device_ids)

                    for device_id in device_ids:
                        id_device = devices.objects.get(id=device_id)
                        insertar_device_status = device_status(
                            deviceId=id_device,
                            shift=shift,
                            lineid=dataline.id,
                            data=5,
                        )
                        insertar_device_status.save()

            except line_status.DoesNotExist:
                pass

                # Handle missing keys or inactive status
        # return JsonResponse({"lineas": lineas})
        # Redirige a la página correspondiente
        return HttpResponseRedirect("../../linemanagement/home")
    else:
        # Handle the case when shift or selected_lines do not have valid values
        pass

    # Handle the case when the request method is not POST

    lineas = list(lines.objects.all().values("name"))
    lineas_devices = {
        line["name"]: [
            device["name"]
            for device in devices.objects.filter(line=line["name"]).values("name")
        ]
        for line in lineas
    }
    print(lineas_devices)
    request.session["lineas"] = lineas
    return render(
        request,
        "login/turno.html",
        {
            "name": name,
            "lineas": lineas,
            "lineas_devices": lineas_devices,
            "usertype": usertype,
            "last_message": last_message,
        },
    )


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = loginUser.objects.get(Q(email__iexact=username))
        except loginUser.DoesNotExist:
            logging.error(
                f"No se encontró el usuario con el correo electrónico: {username}"
            )
            return
        except MultipleObjectsReturned:
            logging.warning(
                f"Se encontraron múltiples usuarios con el mismo correo electrónico: {username}"
            )
            return User.objects.filter(email__iexact=username).order_by("id").first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        else:
            logging.error(f"Contraseña incorrecta para el usuario: {username}")
            return

    def get_user(self, user_id):
        try:
            return loginUser.objects.get(pk=user_id)
        except loginUser.DoesNotExist:
            return None


def error_404_view(request, exception):
    return render(request, "error.html", {})


@login_required
def create_line(request):
    if request.method == "POST":
        new_amount_device = request.POST["amountDevice"]
        new_line = request.POST["line"]

        # Crear la línea en la base de datos
        create_line = lines(name=new_line, amountDevice=new_amount_device)
        create_line.save()

        # Redirigir a la vista "create_devices" con los datos en la URL
        url = f"../create-devices/{new_line}"
        return redirect(url)

    last_line = lines.objects.latest("id")
    palabras = last_line.name.split()
    # Obtener la parte numérica y convertirla a entero
    numero = int(palabras[-1])
    # Sumarle uno al número
    numero += 1
    last_line = "linea " + str(numero)
    return render(request, "login/crear_nueva_linea_datos.html", {"linea": last_line})


@login_required
def create_devices(request, nameLine):
    linea = lines.objects.get(name=nameLine)
    amount_devices = linea.amountDevice

    if request.method == "POST":
        for i in range(amount_devices):
            device_nombre = request.POST.get(
                f"device[{i}]"
            )  # Usar el índice i correctamente
            a = devices(line=nameLine, name=device_nombre, dataType=device_nombre)
            a.save()

        return redirect("shift")

    return render(
        request, "login/crear_nuevo_dispositivo.html", {"amount": range(amount_devices)}
    )


# @login_required
def delete_line(request):
    if request.method == "POST":
        del_line = request.POST["delete-line"]
        nota = request.POST["nota"]
        notes = delete_notes(line=delete_line, note=nota)
        notes.save()

        delete_l = lines.objects.get(name=del_line)
        delete_l.delete()
        return redirect("shift")

    lines_data = lines.objects.values_list("name", flat=True)

    # amount = lines.objects.values_list("amountDevice", flat=True)
    return render(request, "login/eliminar_linea.html", {"lines": lines_data})


# @login_required
def mod_lines(request):
    line = lines.objects.values_list("name", "amountDevice")
    return render(request, "login/modificar_linea_existente.html", {"lines": line})


# @login_required
def mod_devices(request, nameLine):
    linea = lines.objects.get(name=nameLine)
    amount_devices = linea.amountDevice
    name_devices = devices.objects.filter(line=nameLine).values_list("name", "id")
    devices_to_update = []

    if request.method == "POST":
        for i in range(amount_devices):
            device_nombre = request.POST.get(f"device[{i+1}]")
            device_id = request.POST.get(f"id[{i+1}]")
            a = devices.objects.get(line=nameLine, id=device_id)
            a.name = device_nombre
            a.dataType = device_nombre
            devices_to_update.append(a)

            production = device_production.objects.filter(deviceId_id_id=device_id)
            for p in production:
                p.name = device_nombre

        devices.objects.bulk_update(devices_to_update, fields=["name", "dataType"])
        device_production.objects.bulk_update(production, fields=["name"])

        return redirect("shift")
    return render(
        request,
        "login/editar_dispositivos.html",
        {"amountDevice": name_devices},
    )


# @login_required
def menu(request):
    if request.method == "POST":
        name = request.POST["nombre"]
        email = request.POST["correo"]
        sup = supervisor.objects.create(name=name, email=email, type="Mantenimiento")

        return render(request, "login/edicion_lineas.html")

    return render(request, "login/edicion_lineas.html")


def create_user(request):
    if request.method == "POST":
        name = request.POST["nameuser"]
        apellido = request.POST["apellido"]
        email = request.POST["email"]
        cargo = request.POST["cargo"]
        password = make_password(request.POST["pass1"])
        user = loginUser(
            nombre=name,
            email=email,
            apellido=apellido,
            type=cargo,
            is_superuser=cargo,
            password=password,
        )
        user.save()
        return redirect("shift")
    return render(request, "login/registro_de_usuario.html")


def schedule_config(request):
    if request.method == "POST":
        count = config_shift.objects.all().count()
        prueba = []
        for i in range(count):
            name = request.POST.get(f"name[{i+1}]")
            prueba.append(name)
            start_time = request.POST.get(f"start[{i+1}]")
            end_time = request.POST.get(f"end[{i+1}]")
            shift = config_shift.objects.get(name=name)
            shift.startTime = start_time
            shift.endTime = end_time
            shift.save()

        return redirect("shift")
    if request.method == "GET":
        # Get all startTime and endTime values from config_shift
        shifts = config_shift.objects.all()
        start_times = [shift.startTime.strftime("%H:%M:%S") for shift in shifts]
        end_times = [shift.endTime.strftime("%H:%M:%S") for shift in shifts]
        names = [shift.name for shift in shifts]

        # Convert to JSON
        data = {"start_times": start_times, "end_times": end_times, "names": names}
        times = list(zip(start_times, end_times, names))
        context = {"times": times}

    return render(request, "login/config_schedule.html", context)
