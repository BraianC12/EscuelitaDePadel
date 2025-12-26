import json, os
from flask import Flask, jsonify, request
from flask import render_template
from flask import redirect, url_for

app= Flask(__name__) #crea un servidor

@app.route('/')
def principal():
    return render_template("index.html")

#Para que se guarden los datos cuando se cierre el servidor
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            return json.load(f)
    return []

def guardar_usuario():
    with open("usuarios.json", "w") as f:
        json.dump(usuarios, f, indent=4)

usuarios= cargar_usuarios()

#VALIDACION
def validar_usuario(data):
    if "nombre" not in data or data["nombre"] == "":
        return "El campo 'nombre' es obligatorio."

    if "apellido" not in data or data["apellido"] =="":
        return "El campo 'apellido' es obligatorio."
    
    if "edad" not in data or data["edad"] =="":
        return "El campo 'edad' es obligatorio."

    return None #no hay errores

#generar IDs automaticamente
def generar_id():
    if len(usuarios) == 0:
        return "1"

    ultimo_id = int(usuarios[-1]["id"])
    nuevo_id = ultimo_id + 1
    return str(nuevo_id)


#metod POST -> crea un usuario
@app.route("/users", methods=['POST'])
def crear_usuario():
    data = {
        "nombre": request.form.get("nombre"),
        "apellido": request.form.get("apellido"),
        "edad": request.form.get("edad")
    }

    #VALIDACION
    error = validar_usuario(data)
    if error:
        return jsonify("Error: " + error), 400
    
    #Asignar ID automatico
    data["id"] = generar_id()
    data["status"] ="usuario creado"
    usuarios.append(data)
    guardar_usuario()
    
    #redireccion a la lista
    return redirect(url_for("listar_usuarios_html"))


#REDIRECCION A LAS PAGINAS
@app.route("/turnos")
def turnos():
    return render_template("turnos.html")

@app.route("/ubicacion")
def ubicacion():
    return render_template("ubicacion.html")

@app.route("/registrar")
def registrar():
    return render_template("registrar.html")

@app.route("/login")
def login():
    return render_template("login.html")





if __name__ == '__main__':
    app.run(debug=True)
