from django.urls import path, include
from . import views


urlpatterns = [
    path('home', views.control, name="home"),
    path('maintenance', views.maintenance, name='maintenance'),   
]
