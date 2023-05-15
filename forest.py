import json
from subprocess import call
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz
from sklearn.metrics import mean_squared_error

def cargar_datos(ruta):
    with open(ruta, 'r') as f:
        datos = json.load(f)

    x = []
    y = []
    for d in datos:
        if d['servicios'] != 0:
            x.append([d['servicios_inseguros'] / d['servicios']])
        else:
            x.append([0])
        y.append([d['peligroso']])

    return x, y

def contar_dispositivos_peligrosos(predicciones):
    contador = sum(1 for p in predicciones if p >= 0.5)
    return contador

# Cargar datos de entrenamiento y prueba
xTrain, yTrain = cargar_datos('devices_IA_clases.json')
xTest, yTest = cargar_datos('devices_IA_predecir_v2.json')

# Crear el modelo de Random Forest
frst = RandomForestClassifier(max_depth=1, random_state=0, n_estimators=10)

# Entrenar el modelo con los datos de entrenamiento
frst.fit(xTrain, yTrain)

# Realizar predicción en los datos de prueba
yPred = frst.predict(xTest)

# Calcular el error cuadrático medio
error = mean_squared_error(yTest, yPred)

# Contar el número de dispositivos peligrosos
num_peligrosos = contar_dispositivos_peligrosos(yPred)

# Mostrar resultados
print("Resultado del Random Forest:")
print("Error:", error)
print("Número de dispositivos peligrosos:", num_peligrosos)

# Exportar y visualizar los árboles
for i, estimator in enumerate(frst.estimators_):
    export_graphviz(estimator,
                    out_file='tree.dot',
                    rounded=True, proportion=False,
                    class_names=['noPeligroso', 'peligroso'],
                    precision=2, filled=True)
    call(['dot', '-Tpng', 'tree.dot', '-o', f'tree{i}.png', '-Gdpi=600'])
