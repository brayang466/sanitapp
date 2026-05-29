"""Verifica conexión a MySQL sin levantar el servidor web."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app import create_app
from app.extensions import db


def main() -> int:
    app = create_app()
    with app.app_context():
        try:
            fila = db.session.execute(
                text("SELECT DATABASE() AS bd, VERSION() AS version")
            ).mappings().one()
            print("Conexión exitosa.")
            print(f"  Base de datos: {fila['bd']}")
            print(f"  MySQL: {fila['version']}")
            return 0
        except Exception as exc:
            print(f"Error de conexión: {exc}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
