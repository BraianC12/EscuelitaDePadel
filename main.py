from flask import render_template
from flask import redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
from models import db, Alumno
from models import db, Alumno, Admin
from models import db, Pago
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
from datetime import datetime
from flask import session
import os


app= Flask(__name__) #crea un servidor

app.secret_key = "padel2026"
CLAVE = "padel2026"
MONTO_MENSUAL = 30000


mes_actual = datetime.now().month
anio_actual = datetime.now().year

# configuracion SQLlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumnos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# CONFIGURACIONES DE ARCHIVOS
UPLOAD_FOLDER = "static/comprobantes"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024 #5mb
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGHT"] = MAX_FILE_SIZE

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


@app.route("/dashboard")
def dashboard():
    if session.get("rol") != "admin":
        return redirect("/login")
    return render_template("/admin/dashboard.html")


@app.route("/admin/dashboard")
def panel_admin():
    return render_template("admin/dashboard.html")


#Panel para padres
@app.route("/padre/panel_padre")
def panel_padre():
    if session.get("rol") != "padre":
        return redirect("/login")

    alumno = Alumno.query.get(session["alumno_id"])
    
    
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year

    pago = Pago.query.filter_by(
        alumno_id=alumno.id,
        mes = mes_actual,
        anio = anio_actual
    ).first()

    return render_template(
        "padre/panel_padre.html",
        alumno=alumno,
        pago=pago,
        mes = mes_actual,
        anio = anio_actual
    )

@app.route("/padre/info")
def info_padre():
    return render_template("padre/info.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form["dni"]
        password = request.form["clave"]

        #ADMIN
        admin = Admin.query.filter_by(dni=dni).first()
        if admin and password ==  CLAVE:
            session["rol"] = "admin"
            return redirect("/dashboard")
        
        #PADRE
        alumno = Alumno.query.filter_by(dni=dni).first()
        if alumno and password == CLAVE:
            session["rol"] = "padre"
            session["alumno_id"] = alumno.id
            return redirect(url_for("panel_padre"))
        
        flash("Credenciales incorrectas")

    return render_template("login.html")


@app.route("/admin/alumnos")
def admin_alumnos():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    alumnos = Alumno.query.all()
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year

    alumnos_estados = []

    for alumno in alumnos:
        pago = Pago.query.filter_by(
            alumno_id=alumno.id,
            mes=mes_actual,
            anio=anio_actual,
        ).first()

        if pago:
            estado=pago.estado
        else:
            estado="pendiente"

        alumnos_estados.append({
            "alumno":alumno,
            "estado": estado
        })
    
    return render_template("admin/alumnos.html", alumnos_estado=alumnos_estados)

@app.route("/admin")
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        now=date.today().strftime("%d/%m/%Y")
    )

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



# RUTA ADMIN -> TURNOS
@app.route("/admin/turnos")
def admin_turnos():
    turnos = {
        "10:30": Alumno.query.filter_by(turno="10:30").all(),
        "12:00": Alumno.query.filter_by(turno="12:00").all(),
        "13:30": Alumno.query.filter_by(turno="13:30").all()
    }

    return render_template("admin/turnos.html", turnos=turnos)

@app.route("/admin/turnos/cambiar/<int:id>", methods=["POST"])
def cambiar_turno(id):
    alumno = Alumno.query.get_or_404(id)
    nuevo_turno = request.form.get("turno")

    alumno.turno = nuevo_turno
    db.session.commit()

    return redirect(url_for("admin_turnos"))

#PAGOS -> PADRE
MESES_ES_NUM = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}



@app.route("/padre/pagos", methods=["GET", "POST"])
def pagos_padre():

    if session.get("rol") != "padre":
        return redirect("/login")
    
    alumno_id = session["alumno_id"]

    pago = Pago.query.filter_by (
        alumno_id = alumno_id,
        mes = mes_actual,
        anio = anio_actual
    ).first()

    if request.method == "POST":
        archivo = request.files.get("comprobante")

        if not archivo or archivo.filename == "":
            flash("No se seleccionó ningún archivo")
            return redirect(url_for("pagos_padre"))
        
        if not archivo_permitido(archivo.filename):
            flash("Formato no permitido. Usar JPG, PNG o PDF")
            return redirect(url_for("pagos_padre"))
    
        # Año y mes para la carpeta
        anio = datetime.now().year
        mes = f"{datetime.now().month:02d}"

        carpeta_destino = os.path.join(
            app.config["UPLOAD_FOLDER"],
            str(anio),
            mes
        )

        os.makedirs(carpeta_destino, exist_ok=True)

        extension = archivo.filename.rsplit(".", 1)[1].lower()
        nombre_archivo = f"{alumno_id}_{anio}_{mes}.{extension}"

        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
        archivo.save(ruta_completa)

        ruta_relativa = f"{anio}/{mes}/{nombre_archivo}"

        if not pago:
            pago = Pago(
                alumno_id = alumno_id,
                mes = mes_actual,
                anio = anio_actual,
                comprobante = ruta_relativa,
                estado = "enviado"
            )
            db.session.add(pago)
        else:
            pago.comprobante = ruta_relativa
            pago.estado = "enviado"
        
        db.session.commit()
        flash("Comprobante enviado correctamente")
        return redirect(url_for("pagos_padre"))
    
    return render_template(
        "padre/pagos.html",
        pago = pago,
        mes_nombre = MESES_ES_NUM[mes_actual],
        anio= anio_actual,
        monto = MONTO_MENSUAL
    )

@app.route("/admin/pagos")
def admin_pagos():
    if session.get("rol") != "admin":
        return redirect("/login")
    
    pagos = Pago.query.all()

    total_aprobados = 0
    total_pendientes = 0

    for pago in pagos:
        try:
            pago.mes_nombre = MESES_ES_NUM.get(int(pago.mes), "Mes invalido")
        except ValueError:
            pago.mes_nombre = pago.mes

        if pago.estado == "aprobado":
            total_aprobados += 1
        else:
            total_pendientes += 1
        

    return render_template(
        "admin/pagos.html", 
        pagos=pagos,
        total_aprobados=total_aprobados,
        total_pendientes=total_pendientes
        )

@app.route("/admin/pagos/aprobar/<int:id>")
def aprobar_pago(id):
    if session.get("rol") != "admin":
        return redirect("/login")

    pago = Pago.query.get_or_404(id)
    pago.estado = "aprobado"
    db.session.commit()

    return redirect(url_for("admin_pagos"))


@app.route("/padre/pagos/historial")
def historial_pagos_padre():
    if session.get("rol") != "padre":
        return redirect("/login")

    alumno_id = session["alumno_id"]

    pagos = Pago.query.filter_by(
        alumno_id=alumno_id
    ).order_by(Pago.anio.desc(), Pago.id.desc()).all()

    return render_template(
        "padre/historial_pagos.html",
        pagos=pagos
    )

# funcion para validar extensiones
def archivo_permitido(nombre_archivo):
    return (
        "." in nombre_archivo
        and nombre_archivo.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def generar_cuotas_mes_actual(alumno_id):
    hoy = date.today()
    alumno = Alumno.query.get(alumno_id)

    # No generar cuotas anteriores a la fecha de alta
    if alumno.fecha_alta.year > hoy.year:
        return None
    
    if alumno.fecha_alta.year == hoy.year and alumno.fecha_alta.month > hoy.month:
        return None
    
    pago = generar_cuotas_mes_actual(alumno_id)

    if not pago:
        pago = Pago(
            alumno_id=alumno_id,
            mes=hoy.month,
            anio=hoy.year,
            estado = "pendiente"
        )
        db.session.add(pago)
        db.session.commit()
    
    return pago


if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    #app.run(debug=True)
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)
