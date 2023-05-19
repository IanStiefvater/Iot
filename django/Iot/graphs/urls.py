from django.urls import path, include
from . import views

urlpatterns = {
    path('graphs', views.graphs, name="graphs"),
    path('desempeño', views.desempeño, name="desempeño"),
}