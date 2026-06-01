@echo off
chcp 65001 >nul
title SanitApp - Actualizar desde GitHub

set "PROYECTO=D:\proyectos\SanitApp"
cd /d "%PROYECTO%"

echo ============================================
echo   Actualizando SanitApp desde GitHub
echo   %PROYECTO%
echo ============================================
echo.

git pull origin main
if errorlevel 1 (
    echo [ERROR] git pull fallo. Revise conexion y credenciales.
    pause
    exit /b 1
)

echo.
echo Verificando plantilla NO CUMPLE (debe mostrar mark-no):
findstr /C:"mark-no" "%PROYECTO%\app\templates\main\registros.html"
if errorlevel 1 (
    echo [AVISO] No se encontro mark-no en registros.html - el pull puede estar incompleto.
) else (
    echo [OK] Cambio de la X detectado en el codigo.
)

echo.
echo ============================================
echo   IMPORTANTE:
echo   1. Cierre la ventana donde corre SanitApp (Ctrl+C)
echo   2. Vuelva a ejecutar iniciar_sanitapp.bat
echo   3. En el navegador: Ctrl+F5 o ventana privada
echo ============================================
pause
