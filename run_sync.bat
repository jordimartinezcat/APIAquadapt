@echo off
REM =====================================================
REM Script para ejecutar sincronización AquaAdvanced API
REM Para usar en Apache NiFi (ExecuteStreamCommand)
REM =====================================================

cd /d "%~dp0"

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Ejecutar script de sincronización
python sync_scheduledflow_to_db.py

REM Código de salida
exit /b %ERRORLEVEL%
