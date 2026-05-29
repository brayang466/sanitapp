from datetime import datetime


def saludo_por_hora(fecha_hora: datetime | None = None) -> str:
    """Saludo según la hora local del equipo/servidor."""
    ahora = fecha_hora or datetime.now()
    hora = ahora.hour
    if 5 <= hora < 12:
        return "Buenos días"
    if 12 <= hora < 19:
        return "Buenas tardes"
    return "Buenas noches"
