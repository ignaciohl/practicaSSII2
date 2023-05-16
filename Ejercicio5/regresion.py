import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


def cargar_datos(ruta):
    with open(ruta, 'r') as f:
        datos = json.load(f)

    x = [[d['servicios_inseguros'] / d['servicios']] if d['servicios'] != 0 else [0.0] for d in datos]
    y = [[d['peligroso']] for d in datos]

    return x, y


def contar_dispositivos_peligrosos(predicciones):
    contador = sum(1 for p in predicciones if p >= 0.5)
    return contador


def mostrar_grafico(x, y, predicciones):
    plt.scatter(x, y, color="black")
    plt.plot(x, predicciones, color="blue", linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()


def realizar_regresion_lineal(datos_entrenamiento, datos_prueba):
    x_train, y_train = datos_entrenamiento
    x_test, y_test = datos_prueba

    regresion = LinearRegression()
    regresion.fit(x_train, y_train)

    predicciones = regresion.predict(x_test)
    error = mean_squared_error(y_test, predicciones)
    dispositivos_peligrosos = contar_dispositivos_peligrosos(predicciones)

    return predicciones, error, dispositivos_peligrosos


# Cargar datos de entrenamiento y prueba
datos_entrenamiento = cargar_datos('devices_IA_clases.json')
datos_prueba = cargar_datos('devices_IA_predecir_v2.json')

# Realizar regresión lineal
predicciones, error, dispositivos_peligrosos = realizar_regresion_lineal(datos_entrenamiento, datos_prueba)

# Mostrar resultados
print("Resultado de la Regresión Lineal:")
print("Error medio:", error)
print("Número de dispositivos peligrosos:", dispositivos_peligrosos)

# Mostrar gráfico
mostrar_grafico(datos_prueba[0], datos_prueba[1], predicciones)
