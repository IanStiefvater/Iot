import random
import time

# Función para generar datos aleatorios de conteo de botellas
def obtener_conteo_botellas():
    
    return random.randint(200, 5000)
    

# Simular lecturas del sensor cada 5 segundos
contador=0

def ConteoBotellas():
    
   
        conteo_botellas = obtener_conteo_botellas()
        #contador = conteo_botellas + contador
        print("Conteo de botellas: %d" % conteo_botellas)
        #print("total:" ,contador)
      

        return conteo_botellas

while True:
    ConteoBotellas();
    time.sleep(6)


