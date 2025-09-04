"""
Aplicación Web para Transferencia SFTP → GCP
Semi-automatización con botón de inicio manual
"""

from flask import Flask, render_template, jsonify, request
import os
import gzip
import shutil
import tempfile
import paramiko
from datetime import datetime, timedelta
from google.cloud import storage
import re
import logging
from typing import List, Dict, Optional
import json
from pathlib import Path

app = Flask(__name__)

# Configuración
SFTP_CONFIG = {
    'hostname': '10.180.214.22',
    'port': 22,
    'username': 'ftpuser',
    'password': 'PhTimwe.321',
    'remote_directory': '/ruta/archivos'  # Actualizar con la ruta correcta
}

GCP_CONFIG = {
    'project_id': 'beside-352612',  # Proyecto GCP correcto
    'bucket_name': 'xa-entel-data',
    'destination_folder': 'Otros/',
    'service_account_path': 'service-account.json'  # Ruta al archivo de credenciales
}

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferManager:
    def __init__(self):
        self.sftp_client = None
        self.gcp_client = None
        self.bucket = None
        
    def connect_gcp(self):
        """Conectar a Google Cloud Storage"""
        try:
            if os.path.exists(GCP_CONFIG['service_account_path']):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CONFIG['service_account_path']
            
            self.gcp_client = storage.Client(project=GCP_CONFIG['project_id'])
            self.bucket = self.gcp_client.bucket(GCP_CONFIG['bucket_name'])
            logger.info("✅ Conexión GCP establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando GCP: {str(e)}")
            return False
    
    def get_last_upload_date(self) -> Optional[datetime]:
        """Obtener la última fecha de archivos cargados en el bucket"""
        try:
            blobs = self.bucket.list_blobs(prefix=GCP_CONFIG['destination_folder'])
            
            dates = []
            for blob in blobs:
                # Extraer fecha del nombre del archivo
                # Asumir formato: archivo_YYYYMMDD.csv o similar
                filename = blob.name.split('/')[-1]
                date_match = re.search(r'(\d{8})', filename)  # YYYYMMDD
                if date_match:
                    date_str = date_match.group(1)
                    try:
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        dates.append(file_date)
                    except ValueError:
                        continue
            
            if dates:
                last_date = max(dates)
                logger.info(f"📅 Última fecha encontrada en bucket: {last_date.strftime('%Y-%m-%d')}")
                return last_date
            else:
                logger.warning("⚠️  No se encontraron archivos con fecha en el bucket")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo última fecha: {str(e)}")
            return None
    
    def connect_sftp(self):
        """Conectar al servidor SFTP"""
        try:
            transport = paramiko.Transport((SFTP_CONFIG['hostname'], SFTP_CONFIG['port']))
            transport.connect(
                username=SFTP_CONFIG['username'], 
                password=SFTP_CONFIG['password']
            )
            self.sftp_client = paramiko.SFTPClient.from_transport(transport)
            logger.info("✅ Conexión SFTP establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando SFTP: {str(e)}")
            return False
    
    def get_files_to_download(self, start_date: datetime, end_date: datetime) -> List[str]:
        """Obtener lista de archivos a descargar desde SFTP"""
        try:
            # Cambiar al directorio remoto
            self.sftp_client.chdir(SFTP_CONFIG['remote_directory'])
            all_files = self.sftp_client.listdir()
            
            files_to_download = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y%m%d')
                
                # Buscar archivos que contengan esta fecha
                for file in all_files:
                    if date_str in file and file.endswith('.gz'):
                        files_to_download.append(file)
                        
                current_date += timedelta(days=1)
            
            logger.info(f"📁 Archivos encontrados para descargar: {len(files_to_download)}")
            return files_to_download
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo archivos SFTP: {str(e)}")
            return []
    
    def download_and_decompress(self, files: List[str], temp_dir: str) -> List[str]:
        """Descargar y descomprimir archivos"""
        decompressed_files = []
        
        for file in files:
            try:
                # Descargar archivo .gz
                local_gz_path = os.path.join(temp_dir, file)
                self.sftp_client.get(file, local_gz_path)
                logger.info(f"📥 Descargado: {file}")
                
                # Descomprimir archivo
                csv_filename = file.replace('.gz', '')
                local_csv_path = os.path.join(temp_dir, csv_filename)
                
                with gzip.open(local_gz_path, 'rb') as gz_file:
                    with open(local_csv_path, 'wb') as csv_file:
                        shutil.copyfileobj(gz_file, csv_file)
                
                logger.info(f"📦 Descomprimido: {csv_filename}")
                decompressed_files.append(local_csv_path)
                
                # Eliminar archivo .gz temporal
                os.remove(local_gz_path)
                
            except Exception as e:
                logger.error(f"❌ Error procesando archivo {file}: {str(e)}")
                continue
        
        return decompressed_files
    
    def upload_to_gcp(self, local_files: List[str]) -> Dict[str, int]:
        """Subir archivos a GCP"""
        results = {'success': 0, 'failed': 0, 'uploaded_files': []}
        
        for local_file in local_files:
            try:
                filename = os.path.basename(local_file)
                destination_path = GCP_CONFIG['destination_folder'] + filename
                
                blob = self.bucket.blob(destination_path)
                blob.upload_from_filename(local_file)
                
                logger.info(f"☁️ Subido a GCP: {filename}")
                results['success'] += 1
                results['uploaded_files'].append(filename)
                
            except Exception as e:
                logger.error(f"❌ Error subiendo {local_file}: {str(e)}")
                results['failed'] += 1
        
        return results
    
    def cleanup(self):
        """Cerrar conexiones"""
        if self.sftp_client:
            self.sftp_client.close()
        logger.info("🔒 Conexiones cerradas")

# Instancia global del manager
transfer_manager = TransferManager()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/check_status')
def check_status():
    """Verificar estado de conexiones y última fecha"""
    try:
        # Conectar a GCP para verificar última fecha
        if not transfer_manager.connect_gcp():
            return jsonify({
                'success': False,
                'message': 'Error conectando a GCP. Verifica credenciales.'
            })
        
        last_date = transfer_manager.get_last_upload_date()
        
        if last_date:
            # Calcular días pendientes
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            days_pending = (yesterday - last_date).days
            
            return jsonify({
                'success': True,
                'last_upload_date': last_date.strftime('%Y-%m-%d'),
                'days_pending': max(0, days_pending),
                'bucket_accessible': True
            })
        else:
            return jsonify({
                'success': True,
                'last_upload_date': None,
                'days_pending': 0,
                'bucket_accessible': True,
                'message': 'No se encontraron archivos con fecha en el bucket'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error verificando estado: {str(e)}'
        })

@app.route('/api/start_transfer', methods=['POST'])
def start_transfer():
    """Iniciar proceso de transferencia"""
    try:
        # Conectar a GCP
        if not transfer_manager.connect_gcp():
            return jsonify({
                'success': False,
                'message': 'Error conectando a GCP'
            })
        
        # Obtener última fecha
        last_date = transfer_manager.get_last_upload_date()
        if not last_date:
            # Si no hay archivos, empezar desde hace 7 días
            last_date = datetime.now() - timedelta(days=7)
        
        # Calcular rango de fechas
        start_date = last_date + timedelta(days=1)
        end_date = datetime.now() - timedelta(days=1)  # Hasta ayer
        
        if start_date > end_date:
            return jsonify({
                'success': True,
                'message': 'No hay archivos pendientes por procesar',
                'files_processed': 0
            })
        
        # Conectar a SFTP
        if not transfer_manager.connect_sftp():
            return jsonify({
                'success': False,
                'message': 'Error conectando a SFTP. Verifica que la VPN esté conectada.'
            })
        
        # Obtener archivos a descargar
        files_to_download = transfer_manager.get_files_to_download(start_date, end_date)
        
        if not files_to_download:
            return jsonify({
                'success': True,
                'message': f'No se encontraron archivos para el período {start_date.strftime("%Y-%m-%d")} - {end_date.strftime("%Y-%m-%d")}',
                'files_processed': 0
            })
        
        # Crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            # Descargar y descomprimir
            decompressed_files = transfer_manager.download_and_decompress(files_to_download, temp_dir)
            
            if not decompressed_files:
                return jsonify({
                    'success': False,
                    'message': 'Error descargando/descomprimiendo archivos'
                })
            
            # Subir a GCP
            upload_results = transfer_manager.upload_to_gcp(decompressed_files)
        
        # Limpiar conexiones
        transfer_manager.cleanup()
        
        return jsonify({
            'success': True,
            'message': f'Proceso completado exitosamente',
            'files_found': len(files_to_download),
            'files_processed': upload_results['success'],
            'files_failed': upload_results['failed'],
            'uploaded_files': upload_results['uploaded_files'],
            'date_range': f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"
        })
        
    except Exception as e:
        transfer_manager.cleanup()
        logger.error(f"Error en transferencia: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error durante la transferencia: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)