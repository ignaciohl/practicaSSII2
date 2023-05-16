import sqlite3
import json
import pandas as pd
from flask import *
import requests
import hashlib
import flask as fl


#Conectar la bd creada con sqlite
con= sqlite3.connect('practica.db')
#Leer datos proporcionados (fase de extracción)
df_alertas= pd.read_csv('alerts.csv')
d= open("devices.json")
dispositivos= json.load(d)


cur=con.cursor()

#Diseñar las tablas
cur.execute("CREATE TABLE IF NOT EXISTS responsable(nombre TEXT PRIMARY_KEY, telefono TEXT, rol TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS analisis(id TEXT PRIMARY_KEY, puertos_abiertos TEXT, numPuertosAbiertos TEXT, servicios TEXT, servicios_inseguros TEXT, vulnerabilidades_detectadas INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS devices(id TEXT, ip TEXT, localizacion TEXT,responsable_id TEXT, analisis_id TEXT, FOREIGN KEY(responsable_id) REFERENCES responsable(nombre), FOREIGN KEY(analisis_id) REFERENCES analisis(id))")
cur.execute("CREATE TABLE IF NOT EXISTS alerts(timestamp TEXT, sid TEXT, msg TEXT,clasificacion TEXT, prioridad TEXT, protocolo TEXT, origen TEXT, destino TEXT, puerto TEXT  )")
cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")

#Datos tabla alerts
df_alertas.to_sql('alerts',con,if_exists='replace',index=False)

#Datos tabla responsable
cur.execute("INSERT INTO responsable VALUES ('admin', '656445552','Administracion de sistemas')")
cur.execute("INSERT INTO responsable VALUES ('Paco Garcia', '640220120','Direccion')")
cur.execute("INSERT INTO responsable VALUES ('Luis Sanchez', 'None','Desarrollador')")
cur.execute("INSERT INTO responsable VALUES ('admin', '656445552','Administracion de sistemas')")
cur.execute("INSERT INTO responsable VALUES ('admiin', 'None','None')")
cur.execute("INSERT INTO responsable VALUES ('admin', '656445552','Administracion de sistemas')")
cur.execute("INSERT INTO responsable VALUES ('admin','656445552','Administracion de sistemas')")

#Datos tabla analisis
cur.execute("INSERT INTO analisis VALUES(1, '80/TCP, 443/TCP, 3306/TCP, 40000/UDP', 4, 3, 0, 15)")
cur.execute("INSERT INTO analisis VALUES(2, 'None', 0, 0, 0, 4)")
cur.execute("INSERT INTO analisis VALUES(3, '1194/UDP, 8080/TCP,8080/UDP, 40000/UDP',4, 1, 1, 52)")
cur.execute("INSERT INTO analisis VALUES(4, '443/UDP, 80/TCP',2, 1, 0,3)")
cur.execute("INSERT INTO analisis VALUES(5, '80/TCP, 67/UDP, 68/UDP', 3, 2, 2, 12)")
cur.execute("INSERT INTO analisis VALUES(6, '8080/TCP, 3306/TCP, 3306/UDP', 3,2, 0, 2)")
cur.execute("INSERT INTO analisis VALUES(7, '80/TCP, 443/TCP, 9200/TCP, 9300/TCP, 5601/TCP', 5,3, 2, 21)")

#Datos tabla devices
cur.execute("INSERT INTO devices VALUES('web', '172.18.0.0', 'None','admin', 1)")
cur.execute("INSERT INTO devices VALUES('paco_pc', '172.17.0.0', 'Barcelona','Paco Garcia', 2)")
cur.execute("INSERT INTO devices VALUES('luis_pc', '172.19.0.0', 'Madrid','Luis Sanchez', 3)")
cur.execute("INSERT INTO devices VALUES('router1', '172.1.0.0', 'None','admin', 4)")
cur.execute("INSERT INTO devices VALUES('dhcp_server', '172.1.0.1', 'Madrid','admiin', 5)")
cur.execute("INSERT INTO devices VALUES('mysql_db', '172.18.0.1', 'None','admin', 6)")
cur.execute("INSERT INTO devices VALUES('ELK', '172.18.0.2', 'None','admin', 7)")


app= Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ip")
def ip():
    con = sqlite3.connect("practica.db")
    cur = con.cursor()
    num=request.args.get("number_ips")
    cur.execute("SELECT origen, COUNT(*) as num FROM alerts WHERE prioridad = 1 GROUP BY origen ORDER BY num DESC LIMIT ?",(num,))
    resultados=cur.fetchall()
    return render_template("ip.html",num=num,resultados=resultados)

@app.route("/devices")
def devices():
    con = sqlite3.connect("practica.db")
    cur = con.cursor()
    num = request.args.get("number_devices")
    cur.execute("SELECT d.id, SUM(a.servicios_inseguros + a.vulnerabilidades_detectadas) as total FROM devices d JOIN analisis a ON d.analisis_id = a.id GROUP BY d.id ORDER BY total DESC LIMIT ?", (num,))
    resultados = cur.fetchall()
    return render_template("devices.html", num=num, resultados=resultados)

@app.route("/dangerous")
def dangerous():
    con = sqlite3.connect("practica.db")
    cur = con.cursor()
    num = request.args.get("number_dangerous_devices")
    tipo = request.args.get("type_dangerous_devices")
    if tipo=='more':
        cur.execute("SELECT DISTINCT d.id FROM devices d JOIN analisis a ON d.analisis_id = a.id WHERE a.servicios_inseguros / a.servicios > 0.33 LIMIT ?",(num,))
        resultados = cur.fetchall()
        print(resultados)
        return render_template("dangerous.html",num=num,resultados=resultados,type_dangerous_devices=tipo)
    else:
        cur.execute("SELECT DISTINCT d.id FROM devices d JOIN analisis a ON d.analisis_id = a.id WHERE a.servicios_inseguros / a.servicios > 0.33 LIMIT ?",(num,))
        resultados1 = cur.fetchall()
        cur.execute("SELECT DISTINCT d.id FROM devices d JOIN analisis a ON d.analisis_id = a.id WHERE a.servicios_inseguros / a.servicios < 0.33 LIMIT ?",(num,))
        resultados2 = cur.fetchall()
        return render_template("dangerous.html", num=num, resultados1=resultados1,resultados2=resultados2, type_dangerous_devices=tipo)

@app.route("/vulnerabilities")
def vulnerabilities():
    vuln=requests.get('https://cve.circl.lu/api/last')
    resultados = vuln.json()[:10]
    return render_template('vulnerabilities.html', resultados=resultados)

def generate_hash(password):
    randomSalt = 'random_salt'
    password = randomSalt + password
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()
def store_password(username,password):
    con = sqlite3.connect("practica.db")
    cur = con.cursor()
    hashed_pass = generate_hash(password)
    cur.execute("INSERT INTO users VALUES(?, ?)", (username, hashed_pass))
    print("insertado!!")
    con.commit()


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        con = sqlite3.connect("practica.db")
        cur = con.cursor()
        #if flask.request.form['username'].strip() and flask.request.form['password']:
           # user = flask.request.form['username']
          #  password = flask.request.form['password']
         #   return render_template("/")
        #else:
         #   user = None
        #    return render_template("login.html")
        hashed_password = generate_hash(fl.request.form['password'])
        cur.execute("SELECT password FROM users WHERE username=?", (fl.request.form['username'],))
        result = cur.fetchone()
        print(result)
        if result is not None:
            stored_hash = result[0]
            if stored_hash == hashed_password:
                return render_template("index.html")
            else:
                return render_template("login.html")
        else:
            return redirect("/signup")
    return render_template("login.html")

@app.route("/signup",methods = ['GET','POST'])
def signup():
    if request.method == "POST":

        username = fl.request.form['username']
        password = fl.request.form['password']
        store_password(username,password)
        print("hasta aquí")
        #cur.commit()
        return redirect("/login")
    return render_template("signup.html")

if __name__ == '__main__':
    app.run()


























