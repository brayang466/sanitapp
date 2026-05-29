@echo off
chcp 65001 >nul
title SanitApp - Limpieza y desinfeccion

set "PROYECTO=D:\proyectos\SanitApp"
cd /d "%PROYECTO%"

if not exist "%PROYECTO%\.venv\Scripts\activate.bat" (
    echo [ERROR] No se encuentra el entorno virtual en:
    echo   %PROYECTO%\.venv
    echo.
    echo Cree el entorno con: py -m venv .venv
    echo Luego: pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%PROYECTO%\.env" (
    echo [AVISO] No existe el archivo .env
    echo Copie .env.example a .env y configure HOST, PORT y MySQL.
    echo.
    if exist "%PROYECTO%\.env.txt" (
        echo Detectado .env.txt - renombre a .env sin extension .txt
    )
    pause
    exit /b 1
)

call "%PROYECTO%\.venv\Scripts\activate.bat"

echo ============================================
echo   SanitApp iniciando...
echo   Carpeta: %PROYECTO%
echo ============================================
echo.

python "%PROYECTO%\run.py"

if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion termino con errores.
    pause
    exit /b 1
)

pause
