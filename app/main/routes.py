from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from app.auth.decorators import login_required, role_required, usuario_actual
from app.data.catalogos import AREAS, EQUIPOS_SUPERFICIE, FRECUENCIAS
from app.extensions import db
from app.models.registro_formato import RegistroFormato
from app.models.responsable import Responsable
from app.models.usuario import RolUsuario
from app.services.exportar import exportar_excel, exportar_pdf
from app.utils.saludo import saludo_por_hora
from app.services.periodos import (
    etiqueta_periodo,
    inicio_fin_mes,
    inicio_fin_semana,
    parsear_mes,
    resumen_registros,
)

main_bp = Blueprint("main", __name__)


def _contexto_formulario(datos, registro=None):
    return {
        "registro": registro,
        "datos": datos,
        "areas": AREAS,
        "equipos": EQUIPOS_SUPERFICIE,
        "frecuencias": FRECUENCIAS,
        "responsables": Responsable.nombres_activos(),
    }


def _validar_catalogos(datos: dict, registro: RegistroFormato | None = None) -> list[str]:
    errores = []

    def _invalido(valor: str, catalogo: list[str], previo: str | None) -> bool:
        if not valor or valor in catalogo:
            return False
        return not (registro and previo and valor == previo)

    if _invalido(datos["area"], AREAS, registro.area if registro else None):
        errores.append("Seleccione un área válida de la lista.")
    if _invalido(
        datos["equipo_o_superficie"],
        EQUIPOS_SUPERFICIE,
        registro.equipo_o_superficie if registro else None,
    ):
        errores.append("Seleccione un equipo o superficie válido de la lista.")
    if _invalido(datos["frecuencia"], FRECUENCIAS, registro.frecuencia if registro else None):
        errores.append("Seleccione una frecuencia válida de la lista.")
    activos = Responsable.nombres_activos()
    if _invalido(datos["responsable"], activos, registro.responsable if registro else None):
        errores.append("Seleccione un responsable válido de la lista.")
    return errores


def _parse_fecha(valor: str | None) -> date:
    if not valor:
        return date.today()
    return datetime.strptime(valor, "%Y-%m-%d").date()


def _datos_desde_formulario():
    cumplimiento = request.form.get("cumplimiento")
    no_cumple = cumplimiento == "no_cumple"
    return {
        "fecha": _parse_fecha(request.form.get("fecha")),
        "area": (request.form.get("area") or "").strip(),
        "equipo_o_superficie": (request.form.get("equipo_o_superficie") or "").strip(),
        "frecuencia": (request.form.get("frecuencia") or "").strip(),
        "no_cumple": no_cumple,
        "cumple": cumplimiento == "cumple",
        "medida_correctiva": (request.form.get("medida_correctiva") or "").strip() or None,
        "responsable": (request.form.get("responsable") or "").strip(),
    }


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


def _consultar_por_rango(inicio: date, fin: date, frecuencia: str | None = None):
    q = RegistroFormato.query.filter(
        RegistroFormato.fecha >= inicio,
        RegistroFormato.fecha <= fin,
    )
    if frecuencia:
        q = q.filter(RegistroFormato.frecuencia == frecuencia)
    return q.order_by(RegistroFormato.fecha.desc(), RegistroFormato.creado_en.desc()).all()


def _resolver_periodo() -> tuple[str, date, date, dict]:
    periodo = request.args.get("periodo", "diario")
    frecuencia_filtro = request.args.get("frecuencia") or None
    ref = _parse_fecha(request.args.get("fecha"))

    if periodo == "semanal":
        inicio, fin = inicio_fin_semana(ref)
    elif periodo == "mensual":
        anio, mes = parsear_mes(request.args.get("mes"))
        inicio, fin = inicio_fin_mes(anio, mes)
        ref = inicio
    else:
        periodo = "diario"
        inicio = fin = ref

    extra = {
        "frecuencia_filtro": frecuencia_filtro,
        "fecha_ref": ref,
        "mes_ref": f"{inicio.year:04d}-{inicio.month:02d}",
    }
    return periodo, inicio, fin, extra


@main_bp.route("/dashboard")
@login_required
def dashboard():
    hoy = date.today()
    inicio_sem, fin_sem = inicio_fin_semana(hoy)
    inicio_mes, fin_mes = inicio_fin_mes(hoy.year, hoy.month)

    total_hoy = RegistroFormato.query.filter_by(fecha=hoy).count()
    registros_semana = _consultar_por_rango(inicio_sem, fin_sem)
    registros_mes = _consultar_por_rango(inicio_mes, fin_mes)
    resumen_semana = resumen_registros(registros_semana)
    resumen_mes = resumen_registros(registros_mes)

    recientes = (
        RegistroFormato.query.order_by(RegistroFormato.creado_en.desc()).limit(8).all()
    )
    usuario = usuario_actual()
    return render_template(
        "main/dashboard.html",
        hoy=hoy,
        total_hoy=total_hoy,
        resumen_semana=resumen_semana,
        resumen_mes=resumen_mes,
        inicio_sem=inicio_sem,
        fin_sem=fin_sem,
        inicio_mes=inicio_mes,
        recientes=recientes,
        saludo=saludo_por_hora(),
        usuario=usuario,
    )


@main_bp.route("/registros")
@login_required
def listar_registros():
    periodo, inicio, fin, extra = _resolver_periodo()
    registros = _consultar_por_rango(inicio, fin, extra["frecuencia_filtro"])
    resumen = resumen_registros(registros)

    return render_template(
        "main/registros.html",
        registros=registros,
        periodo=periodo,
        inicio=inicio,
        fin=fin,
        etiqueta=etiqueta_periodo(periodo, inicio, fin),
        resumen=resumen,
        frecuencia_filtro=extra["frecuencia_filtro"],
        fecha_ref=extra["fecha_ref"],
        mes_ref=extra["mes_ref"],
        frecuencias_opciones=FRECUENCIAS,
    )


@main_bp.route("/registros/exportar/<formato>")
@login_required
def exportar_registros(formato: str):
    periodo, inicio, fin, extra = _resolver_periodo()
    registros = _consultar_por_rango(inicio, fin, extra["frecuencia_filtro"])
    titulo = f"SanitApp — Registros {etiqueta_periodo(periodo, inicio, fin)}"
    if extra["frecuencia_filtro"]:
        titulo += f" ({extra['frecuencia_filtro']})"

    nombre_base = f"sanitapp_{periodo}_{inicio.isoformat()}"

    if formato == "excel":
        buffer = exportar_excel(registros, titulo)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{nombre_base}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    if formato == "pdf":
        buffer = exportar_pdf(registros, titulo)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{nombre_base}.pdf",
            mimetype="application/pdf",
        )

    flash("Formato de exportación no válido.", "error")
    return redirect(url_for("main.listar_registros", **request.args))


@main_bp.route("/registros/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_registro():
    usuario = usuario_actual()
    if request.method == "POST":
        datos = _datos_desde_formulario()
        errores = []
        if not datos["area"]:
            errores.append("El área es obligatoria.")
        if not datos["equipo_o_superficie"]:
            errores.append("Equipo o superficie es obligatorio.")
        if not datos["frecuencia"]:
            errores.append("La frecuencia es obligatoria.")
        if not datos["responsable"]:
            errores.append("El responsable es obligatorio.")
        if not datos["no_cumple"] and not datos["cumple"]:
            errores.append("Indica si cumple o no cumple.")
        if datos["no_cumple"] and not datos["medida_correctiva"]:
            errores.append("La medida correctiva es obligatoria cuando no cumple.")
        errores.extend(_validar_catalogos(datos, None))

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("main/form_registro.html", **_contexto_formulario(datos))

        registro = RegistroFormato(
            fecha=datos["fecha"],
            area=datos["area"],
            equipo_o_superficie=datos["equipo_o_superficie"],
            frecuencia=datos["frecuencia"],
            no_cumple=datos["no_cumple"],
            cumple=datos["cumple"],
            medida_correctiva=datos["medida_correctiva"],
            responsable=datos["responsable"],
            creado_por_id=usuario.id if usuario else None,
        )
        db.session.add(registro)
        db.session.commit()
        flash("Registro guardado correctamente.", "success")
        return redirect(url_for("main.listar_registros", fecha=datos["fecha"].isoformat()))

    datos_iniciales = {
        "fecha": date.today(),
        "responsable": "",
        "cumple": True,
        "no_cumple": False,
    }
    return render_template("main/form_registro.html", **_contexto_formulario(datos_iniciales))


@main_bp.route("/registros/<int:registro_id>/editar", methods=["GET", "POST"])
@login_required
def editar_registro(registro_id: int):
    registro = RegistroFormato.query.get_or_404(registro_id)
    if request.method == "POST":
        datos = _datos_desde_formulario()
        errores = []
        if not datos["area"]:
            errores.append("El área es obligatoria.")
        if not datos["equipo_o_superficie"]:
            errores.append("Equipo o superficie es obligatorio.")
        if not datos["frecuencia"]:
            errores.append("La frecuencia es obligatoria.")
        if not datos["responsable"]:
            errores.append("El responsable es obligatorio.")
        if not datos["no_cumple"] and not datos["cumple"]:
            errores.append("Indica si cumple o no cumple.")
        if datos["no_cumple"] and not datos["medida_correctiva"]:
            errores.append("La medida correctiva es obligatoria cuando no cumple.")
        errores.extend(_validar_catalogos(datos, registro))

        if errores:
            for e in errores:
                flash(e, "error")
            return render_template(
                "main/form_registro.html", **_contexto_formulario(datos, registro)
            )

        registro.fecha = datos["fecha"]
        registro.area = datos["area"]
        registro.equipo_o_superficie = datos["equipo_o_superficie"]
        registro.frecuencia = datos["frecuencia"]
        registro.no_cumple = datos["no_cumple"]
        registro.cumple = datos["cumple"]
        registro.medida_correctiva = datos["medida_correctiva"]
        registro.responsable = datos["responsable"]
        db.session.commit()
        flash("Registro actualizado.", "success")
        return redirect(url_for("main.listar_registros", fecha=datos["fecha"].isoformat()))

    datos = {
        "fecha": registro.fecha,
        "area": registro.area,
        "equipo_o_superficie": registro.equipo_o_superficie,
        "frecuencia": registro.frecuencia,
        "no_cumple": registro.no_cumple,
        "cumple": registro.cumple,
        "medida_correctiva": registro.medida_correctiva,
        "responsable": registro.responsable,
    }
    return render_template("main/form_registro.html", **_contexto_formulario(datos, registro))


@main_bp.route("/registros/<int:registro_id>/eliminar", methods=["POST"])
@role_required(RolUsuario.ADMIN, RolUsuario.SUPERADMIN)
def eliminar_registro(registro_id: int):
    registro = RegistroFormato.query.get_or_404(registro_id)
    fecha = registro.fecha.isoformat()
    db.session.delete(registro)
    db.session.commit()
    flash("Registro eliminado.", "info")
    return redirect(url_for("main.listar_registros", fecha=fecha))
