from datetime import date, datetime

from app.extensions import db


class RegistroFormato(db.Model):
    __tablename__ = "registros_formato"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column("FECHA", db.Date, nullable=False, default=date.today)
    area = db.Column("AREA", db.String(120), nullable=False)
    equipo_o_superficie = db.Column("EQUIPO_O_SUPERFICIE", db.String(150), nullable=False)
    frecuencia = db.Column("FRECUENCIA", db.String(60), nullable=False)
    no_cumple = db.Column("NO_CUMPLE", db.Boolean, nullable=False, default=False)
    cumple = db.Column("CUMPLE", db.Boolean, nullable=False, default=True)
    medida_correctiva = db.Column("MEDIDA_CORRECTIVA", db.Text, nullable=True)
    responsable = db.Column("RESPONSABLE", db.String(150), nullable=False)
    creado_por_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    creado_por = db.relationship("Usuario", foreign_keys=[creado_por_id])

    @property
    def estado_etiqueta(self) -> str:
        return "Cumple" if self.cumple else "No cumple"
