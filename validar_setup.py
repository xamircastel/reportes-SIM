"""
Script de Validación para Aplicación Web SFTP → GCP
Verifica que todo esté configurado correctamente antes del primer uso
"""

import json
import os
import sys
from datetime import datetime

def print_status(message, status="info"):
    """Imprime mensajes con formato"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "🔍"
    }
    print(f"{icons.get(status, '•')} {message}")

def check_python_version():
    """Verificar versión de Python"""
    print_status("Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor} - Se requiere Python 3.7+", "error")
        return False

def check_dependencies():
    """Verificar dependencias instaladas"""
    print_status("Verificando dependencias...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('paramiko', 'Paramiko'),
        ('google.cloud.storage', 'Google Cloud Storage'),
    ]
    
    missing = []
    for module, name in required_packages:
        try:
            __import__(module)
            print_status(f"{name} - Instalado", "success")
        except ImportError:
            print_status(f"{name} - NO instalado", "error")
            missing.append(name)
    
    if missing:
        print_status("Ejecuta: pip install -r requirements.txt", "warning")
        return False
    
    return True

def check_config_file():
    """Verificar archivo de configuración"""
    print_status("Verificando configuración...")
    
    config_file = "config_web.json"
    if not os.path.exists(config_file):
        print_status(f"Archivo {config_file} no encontrado", "error")
        return False, None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Verificar estructura requerida
        required_sections = ['sftp', 'gcp']
        for section in required_sections:
            if section not in config:
                print_status(f"Sección '{section}' faltante en configuración", "error")
                return False, None
        
        print_status("Archivo de configuración - OK", "success")
        return True, config
        
    except json.JSONDecodeError as e:
        print_status(f"Error en formato JSON: {str(e)}", "error")
        return False, None

def check_gcp_credentials(config):
    """Verificar credenciales de GCP"""
    print_status("Verificando credenciales GCP...")
    
    service_account_path = config.get('gcp', {}).get('service_account_path', 'service-account.json')
    
    if not os.path.exists(service_account_path):
        print_status(f"Archivo {service_account_path} no encontrado", "error")
        print_status("Descarga el archivo desde GCP Console y guárdalo como service-account.json", "warning")
        return False
    
    try:
        # Verificar que es un JSON válido
        with open(service_account_path, 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print_status(f"Campos faltantes en service account: {', '.join(missing_fields)}", "error")
            return False
        
        if creds.get('type') != 'service_account':
            print_status("El archivo no es un service account válido", "error")
            return False
        
        print_status(f"Service Account - OK (Proyecto: {creds.get('project_id')})", "success")
        return True
        
    except json.JSONDecodeError:
        print_status("El archivo service account no es un JSON válido", "error")
        return False
    except Exception as e:
        print_status(f"Error verificando service account: {str(e)}", "error")
        return False

def test_gcp_connection(config):
    """Probar conexión a GCP"""
    print_status("Probando conexión GCP...")
    
    try:
        # Configurar credenciales
        service_account_path = config.get('gcp', {}).get('service_account_path', 'service-account.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        
        from google.cloud import storage
        
        project_id = config['gcp']['project_id']
        bucket_name = config['gcp']['bucket_name']
        
        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        
        # Verificar que el bucket existe y es accesible
        bucket.reload()
        
        print_status(f"Bucket '{bucket_name}' - Accesible", "success")
        
        # Verificar permisos listando algunos objetos
        blobs = list(bucket.list_blobs(prefix=config['gcp']['destination_folder'], max_results=1))
        print_status("Permisos de listado - OK", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Error conectando GCP: {str(e)}", "error")
        print_status("Verifica:", "warning")
        print_status("• Que el project_id sea correcto", "warning")
        print_status("• Que el bucket exista", "warning") 
        print_status("• Que el service account tenga permisos", "warning")
        return False

def test_sftp_info(config):
    """Mostrar información SFTP (sin conectar)"""
    print_status("Información SFTP configurada:")
    
    sftp_config = config.get('sftp', {})
    print(f"  📡 Servidor: {sftp_config.get('hostname')}:{sftp_config.get('port')}")
    print(f"  👤 Usuario: {sftp_config.get('username')}")
    print(f"  📁 Directorio: {sftp_config.get('remote_directory')}")
    print(f"  🔍 Patrón: {sftp_config.get('file_pattern')}")
    
    print_status("⚠️ La conexión SFTP solo se puede probar con VPN conectada", "warning")

def check_file_structure():
    """Verificar estructura de archivos necesarios"""
    print_status("Verificando estructura de archivos...")
    
    required_files = [
        ('app.py', 'Aplicación principal'),
        ('templates/index.html', 'Interfaz web'),
        ('requirements.txt', 'Dependencias'),
        ('config_web.json', 'Configuración')
    ]
    
    missing = []
    for file_path, description in required_files:
        if os.path.exists(file_path):
            print_status(f"{description} - OK", "success")
        else:
            print_status(f"{description} ({file_path}) - Faltante", "error")
            missing.append(file_path)
    
    return len(missing) == 0

def main():
    """Función principal de validación"""
    print("🧪 VALIDACIÓN DE CONFIGURACIÓN - APLICACIÓN WEB SFTP → GCP")
    print("=" * 60)
    print()
    
    # Lista para rastrear resultados
    checks = []
    
    # 1. Verificar Python
    checks.append(("Python", check_python_version()))
    print()
    
    # 2. Verificar dependencias
    checks.append(("Dependencias", check_dependencies()))
    print()
    
    # 3. Verificar estructura de archivos
    checks.append(("Estructura", check_file_structure()))
    print()
    
    # 4. Verificar configuración
    config_ok, config = check_config_file()
    checks.append(("Configuración", config_ok))
    print()
    
    if config:
        # 5. Verificar credenciales GCP
        creds_ok = check_gcp_credentials(config)
        checks.append(("Credenciales GCP", creds_ok))
        print()
        
        # 6. Probar conexión GCP
        if creds_ok:
            gcp_ok = test_gcp_connection(config)
            checks.append(("Conexión GCP", gcp_ok))
            print()
        
        # 7. Mostrar info SFTP
        test_sftp_info(config)
        print()
    
    # Resumen final
    print("=" * 60)
    print("📋 RESUMEN DE VALIDACIÓN:")
    print()
    
    all_ok = True
    for check_name, result in checks:
        status = "✅ OK" if result else "❌ FALLO"
        print(f"  {check_name:20} {status}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 ¡VALIDACIÓN EXITOSA!")
        print("✅ Todo está configurado correctamente")
        print("🚀 Puedes ejecutar: python app.py")
        print("🌐 O usar el script: iniciar_web.bat")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("1. Conectar VPN manualmente")
        print("2. Ejecutar aplicación web")
        print("3. Abrir http://127.0.0.1:5000")
        print("4. ¡Iniciar transferencia!")
    else:
        print("⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("📝 Revisa los errores mostrados arriba")
        print("📖 Consulta guia_web_setup.md para más detalles")
    
    print()
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()