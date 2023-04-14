import plotly.graph_objs as go
import plotly.offline as opy
from django.shortcuts import render

# Create your views here.
def generate_bar_chart():
    # Datos del gráfico
    data = [
        go.Bar(
            x=['Manzanas', 'Plátanos', 'Naranjas'],
            y=[3, 2, 4]
        )
    ]

    # Diseño del gráfico
    layout = go.Layout(
        title='Ejemplo de gráfico de barras',
        xaxis=dict(title='Frutas'),
        yaxis=dict(title='Cantidad')
    )

    # Generar la figura del gráfico
    fig = go.Figure(data=data, layout=layout)

    # Generar la representación HTML del gráfico
    div = opy.plot(fig, auto_open=False, output_type='div')

    return div

def graphs(request):
    # Generar el gráfico
    bar_chart = generate_bar_chart()

    # Renderizar la plantilla HTML con el gráfico generado
    return render(request, 'graphs/graph.html', {'bar_chart': bar_chart})