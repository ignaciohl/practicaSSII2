import json
from sklearn import tree
import graphviz
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
            x.append([0.0])
        y.append([d['peligroso']])

    return x, y

def contar_dispositivos_peligrosos(predicciones):
    contador = sum(1 for p in predicciones if p >= 0.5)
    return contador

# Cargar datos de entrenamiento y prueba
xTrain, yTrain = cargar_datos('devices_IA_clases.json')
xTest, yTest = cargar_datos('devices_IA_predecir_v2.json')

# Crear el modelo de árbol de decisión
clf = tree.DecisionTreeClassifier()

# Entrenar el modelo con los datos de entrenamiento
clf.fit(xTrain, yTrain)

# Realizar predicción en los datos de prueba
print("Resultado del Decision Tree:")
yPred = clf.predict(xTest)

# Calcular el error cuadrático medio
error = mean_squared_error(yTest, yPred)

# Contar el número de dispositivos peligrosos
num_peligrosos = contar_dispositivos_peligrosos(yPred)

# Mostrar resultados
print("Error:", error)
print("Número de dispositivos peligrosos:", num_peligrosos)

# Mostrar el árbol de decisión
dot_data = tree.export_graphviz(clf, out_file=None,
                               feature_names=['porcentage'],
                               class_names=['noPeligroso', 'peligroso'],
                               filled=True, rounded=True,
                               max_depth=1,
                               special_characters=True)
graph = graphviz.Source(dot_data)
graph.render('test.gv', view=True).replace('\\', '/')
