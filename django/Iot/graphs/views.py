from django.shortcuts import render
from lineManagement.models import devices as odevice, graphs as GraphModel, lines as oline

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
    print(results)

    return render(request, "graphs/graph.html", {"results": results})
        