@echo off
echo 🚀 Iniciando aplicación web de transferencia SFTP → GCP
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar que las dependencias están instaladas
echo 📦 Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 📥 Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

REM Verificar que existe el archivo de configuración
if not exist "config_web.json" (
    echo ⚠️  Archivo de configuración no encontrado
    echo 💡 Asegúrate de tener config_web.json configurado
    pause
    exit /b 1
)

REM Verificar que existe el service account de GCP
if not exist "service-account.json" (
    echo ⚠️  Archivo de credenciales GCP no encontrado
    echo 💡 Descarga el archivo service-account.json desde GCP Console
    echo 💡 y colócalo en este directorio
    pause
    exit /b 1
)

echo ✅ Todo listo! Iniciando aplicación web...
echo.
echo 🌐 La aplicación estará disponible en: http://127.0.0.1:5000
echo 📋 Para detener la aplicación, presiona Ctrl+C
echo.

REM Iniciar la aplicación Flask
python app.py

pause