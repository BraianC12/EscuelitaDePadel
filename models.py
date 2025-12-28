from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Alumno(db.Model):
    __tablename__ = "alumnos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), nullable=False, unique=True)
    edad = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Alumno {self.nombre} {self.apellido}>"