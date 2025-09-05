# 🌐 Guía de Configuración - Aplicación Web SFTP → GCP

## 📋 Resumen de la Solución

Has elegido la **opción semi-automática** con aplicación web, ideal para tu caso donde la VPN requiere doble autenticación (2FA).

### 🔄 Flujo del Proceso:
1. **Manual**: Conectar VPN con 2FA
2. **Web**: Abrir aplicación → Click "Iniciar Proceso"
3. **Auto**: Validar última fecha en bucket GCP
4. **Auto**: Conectar SFTP y descargar archivos faltantes
5. **Auto**: Descomprimir archivos .GZ → .CSV
6. **Auto**: Subir archivos al bucket xa-entel-data/Otros

## 🚀 Configuración Paso a Paso

### Paso 1: Instalar Dependencias

```powershell
# Instalar dependencias Python
pip install -r requirements.txt
```

### Paso 2: Configurar Credenciales GCP

#### 2.1 Crear Service Account
1. Ve a [GCP Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Selecciona tu proyecto
3. Crear cuenta de servicio:
   - **Nombre**: `sftp-gcp-transfer`
   - **Descripción**: `Service account para transferencia automática SFTP`

#### 2.2 Asignar Permisos
- **Rol necesario**: `Storage Object Admin` en el bucket `xa-entel-data`
- O crear rol personalizado con permisos:
  - `storage.objects.create`
  - `storage.objects.list`
  - `storage.objects.get`

#### 2.3 Descargar Credenciales
1. En la cuenta de servicio creada → Claves
2. Agregar clave → Crear nueva clave → JSON
3. Guardar como `service-account.json` en el directorio del proyecto

### Paso 3: Configurar Aplicación

#### 3.1 Verificar config_web.json
El archivo ya está configurado con tus datos:

```json
{
    "sftp": {
        "hostname": "10.180.214.22",
        "port": 22,
        "username": "ftpuser",
        "password": "PhTimwe.321",
        "remote_directory": "/",
        "file_pattern": "*.gz"
    },
    "gcp": {
        "project_id": "beside-352612",  // ✅ Configurado correctamente
        "bucket_name": "xa-entel-data",
        "destination_folder": "Otros/"
    }
}
```

✅ **ACTUALIZADO**: El project_id ya está configurado correctamente.

#### 3.2 Estructura de archivos requerida:
```
Reportes-SIM/
├── app.py                     ✅ Aplicación principal
├── service-account.json       ⚠️ REQUERIDO - Descargar de GCP
├── config_web.json           ✅ Configuración
├── requirements.txt          ✅ Dependencias
├── iniciar_web.bat          ✅ Script de inicio
└── templates/
    └── index.html            ✅ Interfaz web
```

## 🧪 Paso 4: Probar la Configuración

### 4.1 Verificar conectividad GCP
```powershell
python -c "
from google.cloud import storage
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'
client = storage.Client()
bucket = client.bucket('xa-entel-data')
bucket.reload()
print('✅ Conexión GCP exitosa')
"
```

### 4.2 Verificar acceso SFTP (con VPN conectada)
```powershell
python -c "
import paramiko
transport = paramiko.Transport(('10.180.214.22', 22))
transport.connect(username='ftpuser', password='PhTimwe.321')
sftp = paramiko.SFTPClient.from_transport(transport)
files = sftp.listdir()
print(f'✅ SFTP conectado. Archivos encontrados: {len(files)}')
sftp.close()
"
```

## 🌐 Paso 5: Ejecutar Aplicación

### 5.1 Inicio Simple
```powershell
# Método 1: Script automático
.\iniciar_web.bat

# Método 2: Manual
python app.py
```

### 5.2 Acceder a la Aplicación
1. Abrir navegador en: **http://127.0.0.1:5000**
2. Verificar que aparezca la interfaz con alertas y estado del sistema

## 🎯 Paso 6: Proceso de Uso Diario

### 6.1 Rutina Diaria:
1. **🔐 Conectar VPN** (manual con 2FA)
2. **🌐 Abrir**: http://127.0.0.1:5000
3. **✅ Verificar estado**:
   - VPN conectada ✅
   - GCP accesible ✅
   - Archivos pendientes (si los hay)
4. **🚀 Click**: "Iniciar Proceso de Transferencia"
5. **📊 Revisar resultados**

### 6.2 Qué hace el proceso automáticamente:
- ✅ Consulta última fecha de archivos en bucket
- ✅ Calcula período faltante (desde última fecha hasta ayer)
- ✅ Conecta al SFTP y lista archivos .gz
- ✅ Descarga archivos del período faltante
- ✅ Descomprime archivos .gz → .csv
- ✅ Sube archivos CSV al bucket xa-entel-data/Otros
- ✅ Limpia archivos temporales
- ✅ Muestra resumen detallado

## 🔧 Personalización

### Cambiar directorio SFTP
Si los archivos están en un subdirectorio específico:

```json
// En config_web.json
"remote_directory": "/ruta/especifica/archivos"
```

### Cambiar patrón de archivos
```json
// En config_web.json
"file_pattern": "reporte_*.gz"  // Para archivos específicos
```

### Configurar proyecto GCP
```json
// En config_web.json - ✅ YA CONFIGURADO
"project_id": "beside-352612"  // ✅ Correcto
```

## 🚨 Solución de Problemas

### Error: "No se pudo conectar al servidor"
- ✅ Verifica que `iniciar_web.bat` esté ejecutándose
- ✅ Comprueba que no hay otros servicios en puerto 5000

### Error: "Error conectando a GCP"
- ✅ Verifica que `service-account.json` existe
- ✅ Comprueba permisos del service account
- ✅ Confirma que `project_id` es correcto

### Error: "Error conectando a SFTP"
- ✅ **VPN debe estar conectada**
- ✅ Verifica conectividad: `ping 10.180.214.22`
- ✅ Confirma credenciales SFTP

### Error: "403 Forbidden" en GCP
- ✅ Service account necesita rol `Storage Object Admin`
- ✅ Verifica que el bucket `xa-entel-data` existe
- ✅ Confirma permisos en la carpeta `Otros/`

## 📊 Logs y Monitoreo

### Ubicación de logs:
- **Consola**: Visible en la terminal donde ejecutas `python app.py`
- **Archivo**: `transfer.log` (si está configurado)

### Logs importantes:
```
✅ Conexión GCP establecida
✅ Conexión SFTP establecida
📅 Última fecha encontrada en bucket: 2025-09-01
📁 Archivos encontrados para descargar: 3
📥 Descargado: archivo_20250902.gz
📦 Descomprimido: archivo_20250902.csv
☁️ Subido a GCP: archivo_20250902.csv
```

## 🎉 ¡Listo!

Con esta configuración tendrás:
- ✅ Interfaz web amigable
- ✅ Proceso semi-automático eficiente
- ✅ Compatibilidad con VPN 2FA
- ✅ Validación automática de fechas
- ✅ Manejo robusto de errores
- ✅ Logs detallados para troubleshooting

**🔗 Próximo paso**: Ejecutar `.\iniciar_web.bat` y visitar http://127.0.0.1:5000