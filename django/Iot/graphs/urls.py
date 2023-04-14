from django.urls import path, include
from . import views

urlpatterns = {
    path('graphs', views.graphs, name="graphs")
}