import os
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.auth.decorators import login_required, usuario_actual
from app.extensions import db

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")

EXTENSIONES_AVATAR = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024


def _carpeta_avatares() -> Path:
    ruta = Path(current_app.root_path) / "static" / "uploads" / "avatars"
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


@perfil_bp.route("/", methods=["GET", "POST"])
@login_required
def mi_perfil():
    usuario = usuario_actual()
    if not usuario:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "password":
            actual = request.form.get("password_actual") or ""
            nueva = request.form.get("password_nueva") or ""
            confirmar = request.form.get("password_confirmar") or ""

            if not usuario.verificar_password(actual):
                flash("La contraseña actual no es correcta.", "error")
            elif len(nueva) < 8:
                flash("La nueva contraseña debe tener al menos 8 caracteres.", "error")
            elif nueva != confirmar:
                flash("Las contraseñas nuevas no coinciden.", "error")
            else:
                usuario.establecer_password(nueva)
                db.session.commit()
                flash("Contraseña actualizada correctamente.", "success")
                return redirect(url_for("perfil.mi_perfil"))

        elif accion == "avatar":
            archivo = request.files.get("avatar")
            if not archivo or not archivo.filename:
                flash("Seleccione una imagen.", "error")
            else:
                ext = Path(secure_filename(archivo.filename)).suffix.lower()
                if ext not in EXTENSIONES_AVATAR:
                    flash("Formato no permitido. Use JPG, PNG o WEBP.", "error")
                else:
                    nombre = f"user_{usuario.id}{ext}"
                    carpeta = _carpeta_avatares()
                    destino = carpeta / nombre
                    if usuario.avatar:
                        anterior = carpeta / usuario.avatar
                        if anterior.exists() and anterior != destino:
                            anterior.unlink(missing_ok=True)
                    archivo.save(destino)
                    if destino.stat().st_size > MAX_AVATAR_BYTES:
                        destino.unlink(missing_ok=True)
                        flash("La imagen no debe superar 2 MB.", "error")
                    else:
                        usuario.avatar = nombre
                        db.session.commit()
                        flash("Foto de perfil actualizada.", "success")
                        return redirect(url_for("perfil.mi_perfil"))

        elif accion == "quitar_avatar":
            if usuario.avatar:
                archivo = _carpeta_avatares() / usuario.avatar
                if archivo.exists():
                    archivo.unlink()
                usuario.avatar = None
                db.session.commit()
                flash("Foto de perfil eliminada.", "info")

        return redirect(url_for("perfil.mi_perfil"))

    return render_template("auth/perfil.html", usuario=usuario)
