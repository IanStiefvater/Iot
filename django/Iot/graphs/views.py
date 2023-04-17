import plotly.graph_objs as go
import plotly.offline as opy
from django.shortcuts import render
from lineManagement.models import devices, device_production
from django.db.models import Count, Sum


# Create your views here.
def generate_bar_chart(namedevices):
    # Datos del gráfico
    graphs = []  # Diccionario para almacenar los gráficos generados

    print("hola", namedevices)
    # Array para almacenar la cantidad de botellas
    # for por cada linea de produccion
    a = 1
    last_object = device_production.objects.order_by("-id").first()
    if last_object == "turno 3":
        shift = "turno 1"
    if last_object == "turno 1":
        shift = "turno 3"
    else:
        shift = "turno 2"
    for i in namedevices:
        results = device_production.objects.filter(
            lineid=a,
        )
        # Agrupa por la columna deviceid y realiza la suma de la producción
        results = results.values("deviceId_id").annotate(
            total_production=Sum("production_data")
        )
        # Ordena los resultados por la columna deviceid_id
        results = results.order_by("deviceId_id")
        # Extrae solo la suma de cada grupo
        sums_list = [result["total_production"] for result in results]
        print("suma", sums_list)
        if sums_list == None:
            for i in range(len(sums_list)):
                sums_list[i] = 0

        data = [
            go.Bar(
                x=namedevices[i],
                # nombres de devices
                y=sums_list,  # cantidad de botellas
            )
        ]

        # Diseño del gráfico
        layout = go.Layout(
            title="Produccion de botellas por linea de produccion",
            xaxis=dict(title="Devices"),
            yaxis=dict(title="Cantidad"),
        )

        # Generar la figura del gráfico
        fig = go.Figure(data=data, layout=layout)

        # Generar la representación HTML del gráfico
        div = opy.plot(fig, auto_open=False, output_type="div")

        # Agregar el gráfico al diccionario con una clave única
        graphs.append(div)  # Usar el nombre del primer dispositivo como clave única
        a = a + 1
    return graphs


def graphs(request):
    # Obtener todos los valores únicos del campo "line"
    lines = devices.objects.values_list("line", flat=True).distinct()

    # Crear un diccionario vacío para almacenar los arrays de nombres
    namedevices = {}

    # Iterar sobre cada línea y obtener los nombres que la comparten
    for line in lines:
        names = devices.objects.filter(line=line).values_list("name", flat=True)
        namedevices[line] = list(names)

    print(lines)
    # Generar el gráfico
    bar_chart = generate_bar_chart(namedevices)

    # Renderizar la plantilla HTML con el gráfico generado
    return render(request, "graphs/graph.html", {"bar_chart": bar_chart})
