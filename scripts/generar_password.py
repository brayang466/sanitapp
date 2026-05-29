"""Genera hash de contraseña para insertar en seed.sql o crear usuarios."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from werkzeug.security import generate_password_hash


def main() -> None:
    password = sys.argv[1] if len(sys.argv) > 1 else "Cambiar123!"
    print(generate_password_hash(password))


if __name__ == "__main__":
    main()
