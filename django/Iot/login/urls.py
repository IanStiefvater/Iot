
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

handler404 = 'lineManagement.views.error_404_view'
urlpatterns = [
    path('login/', views.login_user, name="login"),
    path('shift/', login_required(views.start_shift), name="shift")
]
urlpatterns = list(urlpatterns)
