from django.urls import path
from . import views



handler404 = 'lineManagement.views.error_404_view'
urlpatterns = [
    path('home', views.control, name="home"),
    path('maintenance', views.maintenance, name='maintenance'),
    path('select', views.select, name="select"),
]
