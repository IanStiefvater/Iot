from django.shortcuts import render

def control(request):

    return render(request,"lineManagement/control.html",{})

def maintenance(request):

    return render(request,"lineManagement/maintenance.html",{})
