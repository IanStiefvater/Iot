from django.urls import path
from . import views


""" websocket_urlpatterns = [
    path("ws/data/", GetDeviceDetails.as_asgi()),
] """


handler404 = "lineManagement.views.error_404_view"
urlpatterns = [
    path("home", views.control, name="home"),
    path("maintenance", views.maintenance, name="maintenance"),
    path("select", views.select, name="select"),
    path(
        "lines/<str:lineName>/device/<int:deviceid>/",
        views.device_detail,
        name="device-detail",
    ),
    path(
        "linesdetails/<str:lineName>",
        views.line_detail,
        name="line-detail",
    ),
    path(
        "graph/lines/<str:lineName>/",
        views.graph,
        name="graph",
    ),
    path(
        "shift_hour/",
        views.hour_shift,
        name="shift-hour",
    ),
]
