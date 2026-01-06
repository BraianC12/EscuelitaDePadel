from flask_sqlalchemy import SQLAlchemy
from datetime import date 

db = SQLAlchemy()

class Alumno(db.Model):
    __tablename__ = "alumnos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), nullable=False, unique=True)
    edad = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(20), nullable=False)

    fecha_alta = db.Column(db.Date, default=date.today)

    pagos = db.relationship("Pago", backref="alumno", lazy=True)

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(20), unique=True, nullable=False)


class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"))
    mes = db.Column(db.Integer)
    anio = db.Column(db.Integer)
    monto = db.Column(db.Integer, default=30000)
    comprobante = db.Column(db.String(200))
    estado = db.Column(db.String(20), default="pendiente")