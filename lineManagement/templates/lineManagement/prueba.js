<canvas id="miGrafico" width="800" height="400"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
<script>
    // Función para generar datos aleatorios
    function generarDatosAleatorios(min, max, count) {
        let datos = [];
        for (let i = 0; i < count; i++) {
            datos.push(Math.random() * (max - min) + min);
        }
        return datos;
    }

    // Función para formatear una fecha/hora a HH:mm
    function formatearHora(fecha) {
        return fecha.getHours().toString().padStart(2, '0') + ':' + fecha.getMinutes().toString().padStart(2, '0');
    }

    // Función para crear un rango de tiempo
    function crearRangoTiempo(fechaInicio, intervaloMinutos, duracionMinutos) {
        let tiempo = [];
        let fechaActual = new Date(fechaInicio);
        for (let i = 0; i <= duracionMinutos; i += intervaloMinutos) {
            tiempo.push(new Date(fechaActual));
            fechaActual.setMinutes(fechaActual.getMinutes() + intervaloMinutos);
        }
        return tiempo;
    }

    // Función para interpolar valores
    function interpolarValores(valores, factorInterpolacion) {
        let resultados = [];
        for (let i = 0; i < valores.length - 1; i++) {
            resultados.push(valores[i]);
            let delta = (valores[i + 1] - valores[i]) / factorInterpolacion;
            for (let j = 1; j < factorInterpolacion; j++) {
                resultados.push(valores[i] + delta * j);
            }
        }
        resultados.push(valores[valores.length - 1]); // Añadir el último valor
        return resultados;
    }

    // Generar datos
    let valoresSerie1 = generarDatosAleatorios(100, 200, 24); // Datos cada hora
    let valoresSerie2 = generarDatosAleatorios(50, 150, 24);

    // Crear un rango de tiempo cada minuto para un día
    let fechaInicio = new Date('2023-12-20T00:00:00');
    let rangoTiempo = crearRangoTiempo(fechaInicio, 1, 1440); // 1440 minutos en un día

    // Interpolar valores para cada minuto
    let valoresInterpoladosSerie1 = interpolarValores(valoresSerie1, 60); // 60 minutos entre cada hora
    let valoresInterpoladosSerie2 = interpolarValores(valoresSerie2, 60);

    // Asociar cada valor con su correspondiente hora
    let datosSerie1 = rangoTiempo.map((hora, index) => {
        return { hora: formatearHora(hora), valor: valoresInterpoladosSerie1[index] };
    });
            // Datos simulados como si vinieran de una API
            const datosApiSerie1 = [
                { hora: '2023-12-20T00:20:00', valor: 120 },
                { hora: '2023-12-20T01:30:50', valor: 200 },
                { hora: '2023-12-21T01:30:50', valor: 200 }



            ];

            const datosApiSerie2 = [
                { hora: '2023-12-20T00:00:00', valor: 80 },
                { hora: '2023-12-20T01:00:00', valor: 90 },
                { hora: '2023-12-21T01:30:50', valor: 200 }

    
            ];

            // Convertir la hora de string a objeto Date y formatear los datos para el gráfico
            let datosGraficoSerie1 = datosApiSerie1.map(dato => {
                return { x: new Date(dato.hora), y: dato.valor };
            });

            let datosGraficoSerie2 = datosApiSerie2.map(dato => {
                return { x: new Date(dato.hora), y: dato.valor };
            });

            // ... resto del código para crear el gráfico


function crearGrafico(datosGraficoSerie1, datosGraficoSerie2) {
    const ctx = document.getElementById('miGrafico').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Serie 1',
                data: datosGraficoSerie1,
                borderColor: 'blue',
                fill: false
            }, {
                label: 'Serie 2',
                data: datosGraficoSerie2,
                borderColor: 'red',
                fill: false
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        displayFormats: {
                            minute: 'HH:mm'
                        },
                        tooltipFormat: 'HH:mm'
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 24 // Limitar el número de ticks para evitar el hacinamiento
                    }
                },
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}


    // Asegurarse de que el DOM esté cargado
    document.addEventListener('DOMContentLoaded', (event) => {
        crearGrafico(datosGraficoSerie1, datosGraficoSerie2);
    });
</script>