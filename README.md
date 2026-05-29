# SanitApp

Aplicación para digitalizar el formato diario de **limpieza y desinfección**.

## Campos del formato

| Campo | En base de datos |
|-------|------------------|
| FECHA | `registros_limpieza.fecha` |
| AREA | catálogo `areas` |
| EQUIPO O SUPERFICIE | catálogo `equipos_superficies` |
| FRECUENCIA | catálogo `frecuencias` |
| NO CUMPLE / CUMPLE | `estado_cumplimiento` (`no_cumple` / `cumple`) |
| MEDIDA CORRECTIVA | `medida_correctiva` (obligatoria si no cumple) |
| RESPONSABLE | usuario en `usuarios` |

## Roles

| Rol | Permisos previstos |
|-----|-------------------|
| `superadmin` | Control total, usuarios y configuración |
| `admin` | Catálogos, reportes y supervisión |
| `usuario` | Registro diario de limpieza |

## Base de datos (MySQL Workbench)

1. Abrir **MySQL Workbench** y conectar a su servidor local.
2. **File → Open SQL Script** → `database/schema.sql`
3. Ejecutar el script completo (rayo ⚡ o `Ctrl+Shift+Enter`).
4. Repetir con `database/seed.sql` para datos de prueba.

Consulta del formato en Workbench:

```sql
SELECT * FROM v_registros_formato WHERE FECHA = CURDATE();
```

### Usuarios de prueba (tras seed)

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| superadmin | Cambiar123! | superadmin |
| admin | Cambiar123! | admin |
| usuario | Cambiar123! | usuario |

## Conexión Flask ↔ MySQL

```powershell
cd c:\Users\TIC\SanitApp
copy .env.example .env
# Editar .env con DB_USER y DB_PASSWORD de Workbench
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python scripts\verificar_conexion.py
.\.venv\Scripts\python run.py
```

Probar en el navegador:

- http://127.0.0.1:5000/ — información de la API
- http://127.0.0.1:5000/api/db/ping — prueba de conexión a MySQL

## Estructura del repositorio

```
SanitApp/
├── app/                 # Aplicación Flask
│   ├── models/          # Modelos alineados con el schema SQL
│   └── config.py        # URI MySQL desde variables .env
├── database/
│   ├── schema.sql       # Script principal (Workbench)
│   └── seed.sql         # Datos iniciales
├── scripts/
│   ├── generar_password.py
│   └── verificar_conexion.py
├── run.py
└── requirements.txt
```

## Interfaz web

```powershell
.\.venv\Scripts\python run.py
```

Abrir http://127.0.0.1:5000/auth/login

| Rol | Usuario | Contraseña inicial |
|-----|---------|-------------------|
| Superadmin | superadmin | Cambiar123! |
| Admin | admin | Cambiar123! |
| Usuario | usuario | Cambiar123! |

**Funciones:** panel del día, tabla de registros con filtro por fecha, formulario con todos los campos del formato, gestión de usuarios (admin/superadmin).
