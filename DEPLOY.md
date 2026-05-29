# Despliegue de SanitApp en Windows Server

Guía para instalar la misma aplicación en un servidor Windows (Python + Flask + MySQL).

## Requisitos del servidor

| Componente | Versión recomendada |
|------------|---------------------|
| Windows Server | 2019 o superior |
| Python | 3.11 o 3.12 (64 bits) |
| MySQL | 8.0 (MySQL Workbench en PC de administración) |
| Git | Última versión estable |

## 1. Clonar el repositorio

```powershell
cd C:\inetpub
# o la carpeta que use su empresa, ej: C:\Apps
git clone https://github.com/brayang466/sanitapp.git
cd sanitapp
```

## 2. Entorno virtual e dependencias

```powershell
py -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Variables de entorno

```powershell
copy .env.example .env
notepad .env
```

Ajuste en `.env`:

```env
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=una-clave-larga-y-aleatoria-cambiar

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=su_password_mysql
DB_NAME=sanitapp
```

## 4. Base de datos MySQL

En **MySQL Workbench** conectado al servidor MySQL:

1. Ejecutar `database/instalacion_completa.sql` (instalación nueva), **o** en BD existente:
   - `database/agregar_avatar_usuarios.sql`
   - `database/agregar_responsables.sql`
   - `database/actualizar_admin_paula.sql`
2. Verificar conexión:

```powershell
.\.venv\Scripts\python scripts\verificar_conexion.py
```

## 5. Probar en consola

```powershell
.\.venv\Scripts\activate
python run.py
```

Abrir en el navegador: `http://IP_DEL_SERVIDOR:5000/auth/login`

## 6. Ejecutar como servicio (recomendado)

### Opción A — NSSM (simple)

1. Descargar [NSSM](https://nssm.cc/download) y extraer `nssm.exe`.
2. En PowerShell **como Administrador**:

```powershell
nssm install SanitApp "C:\Apps\sanitapp\.venv\Scripts\python.exe" "C:\Apps\sanitapp\run.py"
nssm set SanitApp AppDirectory "C:\Apps\sanitapp"
nssm set SanitApp AppEnvironmentExtra FLASK_ENV=production
nssm start SanitApp
```

### Opción B — Programador de tareas

- Acción: iniciar programa  
  `C:\Apps\sanitapp\.venv\Scripts\python.exe`  
  Argumentos: `run.py`  
  Iniciar en: `C:\Apps\sanitapp`  
- Ejecutar al iniciar el sistema.

## 7. Firewall

Permitir puerto **5000** (o el definido en `.env`):

```powershell
New-NetFirewallRule -DisplayName "SanitApp" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 8. IIS como proxy (opcional, puerto 80/443)

Si usa IIS con URL amigable:

1. Instalar [URL Rewrite](https://www.iis.net/downloads/microsoft/url-rewrite) y **Application Request Routing**.
2. Habilitar proxy en ARR.
3. Crear sitio que reescriba a `http://127.0.0.1:5000`.

## 9. Carpeta de avatares

La carpeta `app\static\uploads\avatars` debe tener permisos de escritura para la cuenta que ejecuta la app (usuario del servicio NSSM o `IIS AppPool\...`).

## 10. Checklist final

- [ ] `.env` configurado (no subir `.env` a Git)
- [ ] MySQL en ejecución y scripts SQL aplicados
- [ ] `verificar_conexion.py` responde OK
- [ ] Login con `paula.isidro` / contraseña definida
- [ ] Servicio NSSM o tarea en estado **Running**
- [ ] Firewall abierto
- [ ] Respaldo periódico de base `sanitapp`

## Stack del proyecto

- Python 3 + Flask 3
- Flask-SQLAlchemy + PyMySQL
- MySQL 8
- openpyxl / reportlab (exportación Excel y PDF)
- Jinja2 (plantillas HTML)

---

Desarrollado por **Brayan Gómez** — Colbeef / SanitApp.
