from django.shortcuts import render
from lineManagement.models import devices as odevice, graphs as GraphModel, lines as oline, total_maintenance as totalM, device_status as dstatus, line_status as lstatus
from django.db.models import F, ExpressionWrapper, DateTimeField
from django.db.models import DurationField
from django.db.models import Sum, Count
import datetime
import json
from collections import defaultdict
from datetime import timedelta


def graphs(request):

    unique_line_ids = GraphModel.objects.values_list("lineid", flat=True).distinct()
    print(unique_line_ids)
    lines = oline.objects.filter(id__in=unique_line_ids).values_list("id", "name")
    namedevices = {}

    for line_id, line_name in lines:
        names = odevice.objects.filter(line=line_name).values_list("name", flat=True)
        namedevices[line_id] = list(names)

    results = []
    for line_id, devices in namedevices.items():
        line_results = GraphModel.objects.filter(lineid=line_id).values(
            "deviceId__name", "total_production", "potential_production", "shift", "date"
        ).order_by("deviceId_id")

        devices_data = []
        for result in line_results:
            devices_data.append({
                'device_name': result["deviceId__name"],
                'total_production': result["total_production"],
                'potential_production': result["potential_production"],
                'turno':result["shift"],
                'fecha': result["date"].strftime("%Y-%m-%d"),

            })

        line_data = {
            'line_id': line_id,
            'devices_data': devices_data
        }
        results.append(line_data)
    return render(request, "graphs/graph.html", {"results": results})

def convert_date(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    raise TypeError ("Tipo no serializable")


def desempeño(request):
    unique_line_ids = totalM.objects.values_list("lineid", flat=True).distinct()

    total_time_for_lines = []
    total_time_for_devices = []
    total_time_for_points = []

    for line_id in unique_line_ids:
        # Get the line name for the current line ID
        line_name = oline.objects.get(id=line_id).name

        # Get a list of unique device IDs for the current line
        unique_device_ids = odevice.objects.filter(line=line_name).values_list("id", flat=True).distinct()

        line_total_time = 0
        for device_id in unique_device_ids:
            # Get the device name for the current device ID
            device_name = odevice.objects.get(id=device_id).name

            # Get a list of unique points for the current device
            unique_points = totalM.objects.filter(lineid=line_id, deviceId=device_id).values_list("point", flat=True).distinct()

            device_total_time = 0
            for point in unique_points:
                # Filter totalM by deviceId, lineId and point, and sum totalTime
                point_records = totalM.objects.filter(lineid=line_id, deviceId=device_id, point=point)
                point_total_time = point_records.aggregate(Sum("totalTime"))


                # Extract date and shift
                date = point_records.first().date
                shift = point_records.first().shift
                deviceId = point_records.first().deviceId
                lineid = point_records.first().lineid

                # Convert seconds to time
                point_total_time_seconds = point_total_time['totalTime__sum']

                # Add the total time of the point to the total time of the device
                device_total_time += point_total_time_seconds

                total_time_for_points.append({
                    "deviceId": deviceId,
                    "lineId":lineid,
                    "point_name": point,
                    "total_time": point_total_time_seconds,
                    "date": date.strftime("%Y-%m-%d"),
                    "shift": shift
                })

            # Add the total time of the device to the total time of the line
            line_total_time += device_total_time

            total_time_for_devices.append({
                "device_id": device_id,
                "device_name": device_name,
                "lineId": line_id,
                "total_time": device_total_time,
                "date": date.strftime("%Y-%m-%d"),
                "shift": shift
            })

        # Add the total time for the line to the list
        total_time_for_lines.append({
            "line_name": line_name,
            "total_time": line_total_time,
            "date": date.strftime("%Y-%m-%d"),
            "shift": shift
        })

    total_time_for_device_statuses = []

    unique_device_ids = dstatus.objects.values_list("deviceId", flat=True).distinct()
    for device_id in unique_device_ids:
        # Get the device name for the current device ID
        device_name = odevice.objects.get(id=device_id).name


        device_status_results = dstatus.objects.filter(deviceId=device_id).annotate(
            total_time=ExpressionWrapper(F('endTime') - F('starTime'), output_field=DurationField())
        )
        for result in device_status_results:
            # Convert timedelta to seconds
            total_seconds = result.total_time.total_seconds()

            # Extract date from starTime
            date_start = result.starTime.date()
            shift_start = result.shift
            line_id = result.lineid

            total_time_for_device_statuses.append({
                "device_id": result.deviceId_id,
                "device_name": device_name,
                "lineId": line_id,
                "total_time": total_seconds,
                "date": date_start.strftime("%Y-%m-%d"),
                "shift": shift_start
            })

    total_time_for_line_statuses = []

    unique_line_names = oline.objects.values_list("name", flat=True).distinct()
    for line_name in unique_line_names:
        line_status_results = lstatus.objects.filter(lineName=line_name).annotate(
            total_time=ExpressionWrapper(F('endTime') - F('starTime'), output_field=DurationField())
        )
        for result in line_status_results:
            # Convert timedelta to seconds
            total_seconds = result.total_time.total_seconds()

            # Extract date from starTime
            date_start = result.starTime.date()
            shift_start = result.shift

            total_time_for_line_statuses.append({
                "line_name": result.lineName,
                "total_time": total_seconds,
                "date": date_start.strftime("%Y-%m-%d"),
                "shift": shift_start
            })
    print(total_time_for_line_statuses)
   
    
    return render(request, "graphs/desempeño.html", {
    "total_time_for_lines": total_time_for_lines,
    "total_time_for_device_statuses": total_time_for_device_statuses,
    "total_time_for_line_statuses": total_time_for_line_statuses,
    "total_time_for_devices": total_time_for_devices,
    "total_time_for_points": total_time_for_points,})
#procesar segundos a horas minutos y segundos
