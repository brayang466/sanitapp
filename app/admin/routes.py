from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.auth.decorators import role_required, superadmin_required
from app.extensions import db
from app.models.responsable import Responsable
from app.models.usuario import RolUsuario, Usuario

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/usuarios")
@superadmin_required
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.rol, Usuario.username).all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@superadmin_required
def nuevo_usuario():
    if request.method == "POST":
        nombre = (request.form.get("nombre_completo") or "").strip()
        email = (request.form.get("email") or "").strip()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        rol = request.form.get("rol", RolUsuario.USUARIO.value)

        if not all([nombre, email, username, password]):
            flash("Completa todos los campos obligatorios.", "error")
        elif Usuario.query.filter((Usuario.email == email) | (Usuario.username == username)).first():
            flash("El email o usuario ya existe.", "error")
        else:
            usuario = Usuario(
                nombre_completo=nombre,
                email=email,
                username=username,
                rol=RolUsuario(rol),
            )
            usuario.establecer_password(password)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("admin.listar_usuarios"))

    return render_template("admin/form_usuario.html", usuario=None)


@admin_bp.route("/usuarios/<int:usuario_id>/toggle", methods=["POST"])
@superadmin_required
def toggle_usuario(usuario_id: int):
    from app.auth.decorators import usuario_actual

    usuario = Usuario.query.get_or_404(usuario_id)
    actual = usuario_actual()
    if actual and usuario.id == actual.id:
        flash("No puedes desactivar tu propia cuenta.", "error")
        return redirect(url_for("admin.listar_usuarios"))
    usuario.activo = not usuario.activo
    db.session.commit()
    estado = "activado" if usuario.activo else "desactivado"
    flash(f"Usuario {estado}.", "success")
    return redirect(url_for("admin.listar_usuarios"))


@admin_bp.route("/responsables")
@role_required(RolUsuario.SUPERADMIN, RolUsuario.ADMIN)
def listar_responsables():
    responsables = Responsable.query.order_by(Responsable.activo.desc(), Responsable.nombre_completo).all()
    return render_template("admin/responsables.html", responsables=responsables)


@admin_bp.route("/responsables/nuevo", methods=["POST"])
@role_required(RolUsuario.SUPERADMIN, RolUsuario.ADMIN)
def nuevo_responsable():
    nombre = " ".join((request.form.get("nombre_completo") or "").upper().split())
    if not nombre:
        flash("Ingrese el nombre completo del responsable.", "error")
        return redirect(url_for("admin.listar_responsables"))

    existente = Responsable.query.filter_by(nombre_completo=nombre).first()
    if existente:
        if existente.activo:
            flash("Ese responsable ya está en la lista.", "warning")
        else:
            existente.activo = True
            db.session.commit()
            flash("Responsable reactivado en la lista.", "success")
        return redirect(url_for("admin.listar_responsables"))

    db.session.add(Responsable(nombre_completo=nombre))
    db.session.commit()
    flash("Responsable agregado correctamente.", "success")
    return redirect(url_for("admin.listar_responsables"))


@admin_bp.route("/responsables/<int:responsable_id>/toggle", methods=["POST"])
@role_required(RolUsuario.SUPERADMIN, RolUsuario.ADMIN)
def toggle_responsable(responsable_id: int):
    responsable = Responsable.query.get_or_404(responsable_id)
    responsable.activo = not responsable.activo
    db.session.commit()
    if responsable.activo:
        flash(f"{responsable.nombre_completo} activado en la lista.", "success")
    else:
        flash(
            f"{responsable.nombre_completo} retirado de la lista. "
            "Los registros anteriores conservan su nombre.",
            "info",
        )
    return redirect(url_for("admin.listar_responsables"))


@admin_bp.route("/responsables/<int:responsable_id>/eliminar", methods=["POST"])
@role_required(RolUsuario.SUPERADMIN)
def eliminar_responsable(responsable_id: int):
    responsable = Responsable.query.get_or_404(responsable_id)
    db.session.delete(responsable)
    db.session.commit()
    flash("Responsable eliminado del catálogo.", "info")
    return redirect(url_for("admin.listar_responsables"))
