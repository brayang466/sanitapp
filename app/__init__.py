import os

from flask import Flask, jsonify, redirect, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import config_by_name
from app.extensions import db
from app.models.usuario import RolUsuario


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    db.init_app(app)

    from app import models  # noqa: F401

    from app.admin.routes import admin_bp
    from app.auth.perfil import perfil_bp
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    register_api_routes(app)
    register_context(app)

    return app


def register_context(app: Flask) -> None:
    from app.auth.decorators import usuario_actual
    from app.utils.saludo import saludo_por_hora

    @app.context_processor
    def inject_globals():
        return {
            "usuario_actual": usuario_actual(),
            "RolUsuario": RolUsuario,
            "saludo_horario": saludo_por_hora(),
            "static_v": app.config.get("STATIC_VERSION", "1"),
        }


def register_api_routes(app: Flask) -> None:
    @app.get("/api/salud")
    def salud():
        return jsonify({"estado": "ok"})

    @app.get("/api/db/ping")
    def ping_bd():
        try:
            resultado = db.session.execute(
                text("SELECT DATABASE() AS bd, NOW() AS servidor_hora")
            ).mappings().one()
            tablas = db.session.execute(
                text(
                    """
                    SELECT COUNT(*) AS total
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    """
                )
            ).scalar()
            return jsonify(
                {
                    "conectado": True,
                    "base_datos": resultado["bd"],
                    "hora_servidor": str(resultado["servidor_hora"]),
                    "tablas_en_bd": tablas,
                }
            )
        except SQLAlchemyError as exc:
            return (
                jsonify({"conectado": False, "error": str(exc.__cause__ or exc)}),
                503,
            )
