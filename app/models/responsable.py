from datetime import datetime

from app.extensions import db


class Responsable(db.Model):
    __tablename__ = "responsables"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), unique=True, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @staticmethod
    def nombres_activos() -> list[str]:
        return [
            r.nombre_completo
            for r in Responsable.query.filter_by(activo=True)
            .order_by(Responsable.nombre_completo)
            .all()
        ]
