# Test Script - Verificación de Conectividad

"""
Script de prueba para verificar conectividad antes de implementar la automatización completa
"""

import json
import logging
import paramiko
import tempfile
from google.cloud import storage
import os

def test_sftp_connection(config):
    """Prueba la conexión SFTP"""
    print("🔍 Probando conexión SFTP...")
    
    try:
        transport = paramiko.Transport((config['sftp']['hostname'], config['sftp']['port']))
        
        if 'private_key_path' in config['sftp']:
            private_key = paramiko.RSAKey.from_private_key_file(config['sftp']['private_key_path'])
            transport.connect(username=config['sftp']['username'], pkey=private_key)
        else:
            transport.connect(username=config['sftp']['username'], password=config['sftp']['password'])
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Probar listar directorio
        remote_dir = config['sftp']['remote_directory']
        sftp.chdir(remote_dir)
        files = sftp.listdir()
        
        print(f"✅ Conexión SFTP exitosa")
        print(f"📁 Directorio: {remote_dir}")
        print(f"📄 Archivos encontrados: {len(files)}")
        
        # Mostrar algunos archivos CSV
        csv_files = [f for f in files if f.endswith('.csv')][:5]
        if csv_files:
            print(f"📋 Archivos CSV (primeros 5): {', '.join(csv_files)}")
        else:
            print("⚠️  No se encontraron archivos CSV")
        
        sftp.close()
        transport.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión SFTP: {str(e)}")
        return False

def test_gcp_connection(config):
    """Prueba la conexión con GCP Storage"""
    print("\n🔍 Probando conexión GCP Storage...")
    
    try:
        # Configurar credenciales
        if 'service_account_path' in config['gcp']:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['gcp']['service_account_path']
        
        client = storage.Client(project=config['gcp']['project_id'])
        bucket = client.bucket(config['gcp']['bucket_name'])
        
        # Verificar que el bucket existe y es accesible
        bucket.reload()
        
        print(f"✅ Conexión GCP exitosa")
        print(f"📁 Bucket: {config['gcp']['bucket_name']}")
        print(f"🏷️  Proyecto: {config['gcp']['project_id']}")
        
        # Probar crear un archivo de prueba
        test_blob_name = config['gcp']['destination_folder'] + 'test_connection.txt'
        test_blob = bucket.blob(test_blob_name)
        
        test_content = f"Test de conexión - {str(datetime.datetime.now())}"
        test_blob.upload_from_string(test_content)
        
        print(f"✅ Archivo de prueba creado: gs://{config['gcp']['bucket_name']}/{test_blob_name}")
        
        # Eliminar archivo de prueba
        test_blob.delete()
        print(f"🗑️  Archivo de prueba eliminado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión GCP: {str(e)}")
        return False

def test_end_to_end(config):
    """Prueba transferencia completa de un archivo pequeño"""
    print("\n🔍 Probando transferencia completa...")
    
    try:
        # Crear archivo de prueba local
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("col1,col2,col3\n")
            temp_file.write("test,data,123\n")
            temp_file_path = temp_file.name
        
        print(f"📄 Archivo de prueba creado: {temp_file_path}")
        
        # Subir a GCP
        if 'service_account_path' in config['gcp']:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['gcp']['service_account_path']
        
        client = storage.Client(project=config['gcp']['project_id'])
        bucket = client.bucket(config['gcp']['bucket_name'])
        
        test_blob_name = config['gcp']['destination_folder'] + 'test_transfer.csv'
        blob = bucket.blob(test_blob_name)
        blob.upload_from_filename(temp_file_path)
        
        print(f"✅ Archivo subido exitosamente: gs://{config['gcp']['bucket_name']}/{test_blob_name}")
        
        # Verificar que existe
        blob.reload()
        print(f"📊 Tamaño del archivo: {blob.size} bytes")
        
        # Limpiar
        blob.delete()
        os.unlink(temp_file_path)
        
        print(f"🗑️  Archivos de prueba eliminados")
        print(f"✅ Prueba completa exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba completa: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DE CONECTIVIDAD")
    print("=" * 50)
    
    # Cargar configuración
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config.json")
        print("💡 Copia config.json.example a config.json y configúralo con tus datos")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error en formato JSON: {str(e)}")
        return
    
    # Ejecutar pruebas
    results = {
        'sftp': test_sftp_connection(config),
        'gcp': test_gcp_connection(config),
    }
    
    # Solo hacer prueba end-to-end si ambas conexiones funcionan
    if results['sftp'] and results['gcp']:
        results['end_to_end'] = test_end_to_end(config)
    else:
        results['end_to_end'] = False
        print("\n⚠️  Saltando prueba completa debido a errores de conectividad")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  SFTP: {'✅ OK' if results['sftp'] else '❌ FALLO'}")
    print(f"  GCP:  {'✅ OK' if results['gcp'] else '❌ FALLO'}")
    print(f"  E2E:  {'✅ OK' if results['end_to_end'] else '❌ FALLO'}")
    
    if all(results.values()):
        print("\n🎉 ¡Todas las pruebas pasaron! Puedes proceder con la automatización.")
    else:
        print("\n⚠️  Hay errores que necesitas resolver antes de automatizar.")
        print("\n💡 Consejos para solucionar problemas:")
        if not results['sftp']:
            print("  - Verifica que la VPN esté conectada")
            print("  - Revisa credenciales SFTP en config.json")
            print("  - Confirma que el directorio remoto existe")
        if not results['gcp']:
            print("  - Verifica credenciales del service account")
            print("  - Confirma permisos en el bucket de GCP")
            print("  - Revisa que el proyecto y bucket existan")

if __name__ == "__main__":
    import datetime
    main()