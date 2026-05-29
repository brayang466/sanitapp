from datetime import datetime
from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class RolUsuario(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USUARIO = "usuario"


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(
        db.Enum(RolUsuario, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RolUsuario.USUARIO,
    )
    activo = db.Column(db.Boolean, nullable=False, default=True)
    avatar = db.Column(db.String(255), nullable=True)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def establecer_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def es_superadmin(self) -> bool:
        return self.rol == RolUsuario.SUPERADMIN

    @property
    def es_admin(self) -> bool:
        return self.rol in (RolUsuario.SUPERADMIN, RolUsuario.ADMIN)

    def url_avatar(self) -> str | None:
        if self.avatar:
            return f"/static/uploads/avatars/{self.avatar}"
        return None

    def iniciales_avatar(self) -> str:
        partes = self.nombre_completo.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return self.nombre_completo[:2].upper() if self.nombre_completo else "?"
