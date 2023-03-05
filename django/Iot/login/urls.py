
from django.urls import path, include
from . import views


urlpatterns = [
    path('login/', views.login_user, name="login"),
    path('shift/', views.start_shift, name="shift")
]
