import calendar
from datetime import date, datetime, timedelta


def inicio_fin_semana(ref: date) -> tuple[date, date]:
    inicio = ref - timedelta(days=ref.weekday())
    fin = inicio + timedelta(days=6)
    return inicio, fin


def inicio_fin_mes(anio: int, mes: int) -> tuple[date, date]:
    ultimo = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, 1), date(anio, mes, ultimo)


def parsear_mes(valor: str | None) -> tuple[int, int]:
    hoy = date.today()
    if not valor:
        return hoy.year, hoy.month
    partes = valor.split("-")
    return int(partes[0]), int(partes[1])


_MESES = (
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
)


def etiqueta_periodo(periodo: str, inicio: date, fin: date) -> str:
    if periodo == "diario":
        return inicio.strftime("%d/%m/%Y")
    if periodo == "semanal":
        return f"{inicio.strftime('%d/%m')} – {fin.strftime('%d/%m/%Y')}"
    return f"{_MESES[inicio.month - 1]} {inicio.year}"


def resumen_registros(registros) -> dict:
    total = len(registros)
    cumple = sum(1 for r in registros if r.cumple)
    no_cumple = sum(1 for r in registros if r.no_cumple)
    por_frecuencia: dict[str, int] = {}
    for r in registros:
        por_frecuencia[r.frecuencia] = por_frecuencia.get(r.frecuencia, 0) + 1
    return {
        "total": total,
        "cumple": cumple,
        "no_cumple": no_cumple,
        "por_frecuencia": por_frecuencia,
    }
