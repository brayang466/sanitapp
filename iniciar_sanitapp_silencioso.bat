@echo off
REM Inicia SanitApp minimizado (sin ventana visible). Para servicio manual.
cd /d "D:\proyectos\SanitApp"
call ".venv\Scripts\activate.bat"
start "SanitApp" /MIN python run.py
