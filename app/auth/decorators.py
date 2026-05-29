from functools import wraps

from flask import flash, redirect, session, url_for

from app.models.usuario import RolUsuario, Usuario


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def superadmin_required(view):
    return role_required(RolUsuario.SUPERADMIN)(view)


def role_required(*roles: RolUsuario):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            usuario = Usuario.query.get(session["user_id"])
            if not usuario or usuario.rol not in roles:
                flash("No tienes permiso para esta acción.", "error")
                return redirect(url_for("main.dashboard"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def usuario_actual() -> Usuario | None:
    uid = session.get("user_id")
    if not uid:
        return None
    return Usuario.query.get(uid)
