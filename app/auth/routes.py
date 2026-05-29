from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        usuario = Usuario.query.filter_by(username=username, activo=True).first()
        if usuario and usuario.verificar_password(password):
            session.clear()
            session["user_id"] = usuario.id
            session["username"] = usuario.username
            session["rol"] = usuario.rol.value
            session["nombre"] = usuario.nombre_completo
            usuario.ultimo_acceso = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("main.dashboard"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
