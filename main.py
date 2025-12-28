from flask import render_template
from flask import redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from models import db, Alumno


app= Flask(__name__) #crea un servidor

# configuracion SQLlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumnos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#REDIRECCION A LAS PAGINAS
@app.route('/')
def principal():
    return render_template("index.html")

@app.route("/turnos")
def turnos():
    return render_template("turnos.html")

@app.route("/ubicacion")
def ubicacion():
    return render_template("ubicacion.html")

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        dni = request.form.get("dni")
        edad = request.form.get("edad")
        turno = request.form.get("turno")

        nuevo_alumno = Alumno(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            edad=int(edad),
            turno=turno
        )

        db.session.add(nuevo_alumno)
        db.session.commit()

        print("Alumno guardado")

        return redirect(url_for("registrar"))
    
    return render_template("registrar.html")

@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)
