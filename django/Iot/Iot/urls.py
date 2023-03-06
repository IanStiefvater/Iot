<<<<<<< HEAD
=======

>>>>>>> origin
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
<<<<<<< HEAD
    path('authenticate/', include('login.urls')),
    path('linemanagement/', include('lineManagement.urls')),
=======
    path('authenticate/', include('login.urls'), name="shift"),
    # path('linemanagement/', include('lineManagement.urls')),
>>>>>>> origin

]
