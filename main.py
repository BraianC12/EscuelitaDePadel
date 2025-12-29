from flask import render_template
from flask import redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from models import db, Alumno
from models import db, Alumno, Admin
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date

app= Flask(__name__) #crea un servidor

CLAVE_ADMIN = "padel2026"

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form.get("dni")
        clave = request.form.get("clave")

        admin = Admin.query.filter_by(dni=dni).first()

        if admin and clave == CLAVE_ADMIN:
            return redirect(url_for("panel_admin"))
        else:
            flash("DNI o clave incorrectos")

    return render_template("login.html")

@app.route("/admin")
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        now=date.today().strftime("%d/%m/%Y")
    )

@app.route("/admin/alumnos")
def admin_alumnos():
    alumnos = Alumno.query.all()
    return render_template("admin/alumnos.html", alumnos=alumnos)

@app.route("/admin/alumnos/editar/<int:id>", methods=["GET", "POST"])
def editar_alumno(id):
    alumno = Alumno.query.get_or_404(id)

    if request.method == "POST":
        alumno.nombre = request.form["nombre"]
        alumno.apellido = request.form["apellido"]
        alumno.edad = request.form["edad"]
        alumno.turno = request.form["turno"]

        db.session.commit()
        return redirect(url_for("admin_alumnos"))
    
    return render_template("admin/editar_alumno.html", alumno=alumno)

if __name__ == '__main__':
    app.run(debug=True)
