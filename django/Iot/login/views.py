from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse


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
