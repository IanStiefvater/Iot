from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

handler404 = "lineManagement.views.error_404_view"
urlpatterns = [
    path("login/", views.login_user, name="login"),
    path("shift/", login_required(views.start_shift), name="shift"),
    path("recoverpass/", views.recover_passwd, name="rcvpass1"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("create-devices/<str:nameLine>", views.create_devices, name="new-device"),
    path("create-line/", views.create_line, name="create-line"),
    path("create-user/", views.create_user, name="create-user"),
    path("mod-line/", views.mod_lines, name="mod-line"),
    path("mod-devices/<str:nameLine>", views.mod_devices, name="mod-devices"),
    path("change-line/", views.mod_lines, name="change-line"),
    path("delete-line/", views.delete_line, name="delete-line"),
    path("menu/", views.menu, name="menu"),
    path("schedule_config", views.schedule_config, name="schedule_config"),
    # path("menu/", views.menu, name="menu"),
]
urlpatterns = list(urlpatterns)
