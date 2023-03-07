<<<<<<< HEAD


=======
>>>>>>> ae36d42776af4bf94f49dbc37065c731623da627
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
<<<<<<< HEAD

    path('authenticate/', include('login.urls')),
    path('linemanagement/', include('lineManagement.urls')),


    # path('linemanagement/', include('lineManagement.urls')),

=======
    path('authenticate/', include('login.urls')),
    path('linemanagement/', include('lineManagement.urls')),
    path('authenticate/', include('login.urls'), name="shift"),
    # path('linemanagement/', include('lineManagement.urls')),
>>>>>>> ae36d42776af4bf94f49dbc37065c731623da627

]
