# 🌐 Aplicación Web SFTP → GCP Storage

Solución **semi-automática** para transferir archivos CSV desde servidor SFTP (con VPN 2FA) hacia bucket de Google Cloud Storage.

## 📋 Resumen del Problema

- **Situación actual**: Proceso manual diario
- **Origen**: Archivos CSV comprimidos (.gz) en SFTP 10.180.214.22
- **Acceso**: Requiere VPN con doble autenticación (2FA)
- **Destino**: Bucket xa-entel-data/Otros en GCP
- **Objetivo**: Semi-automatización con interfaz web

## 🚀 Solución Implementada

### ✅ Opción Elegida: Aplicación Web Semi-Automática
- ✅ Compatible con VPN 2FA (conexión manual)
- ✅ Interfaz web amigable con un click
- ✅ Automatización completa del resto del proceso
- ✅ Validación inteligente de fechas
- ✅ Descompresión automática .gz → .csv

### 🔄 Flujo del Proceso:
1. **🔐 Manual**: Conectar VPN con 2FA
2. **🌐 Web**: Abrir http://127.0.0.1:5000 → Click "Iniciar Proceso"
3. **🤖 Auto**: Validar última fecha en bucket GCP
4. **🤖 Auto**: Conectar SFTP (10.180.214.22:22)
5. **🤖 Auto**: Descargar archivos .gz faltantes (desde última fecha hasta ayer)
6. **🤖 Auto**: Descomprimir archivos .gz → .csv
7. **🤖 Auto**: Subir archivos CSV al bucket xa-entel-data/Otros

## 📁 Estructura del Proyecto

```
Reportes-SIM/
├── 🌐 app.py                    # Aplicación web Flask
├── 🧪 validar_setup.py          # Script de validación
├── ⚙️  config_web.json          # Configuración específica
├── 🔑 service-account.json      # Credenciales GCP (requerido)
├── 📋 requirements.txt          # Dependencias Python
├── 🚀 iniciar_web.bat           # Script de inicio automático
├── 📁 templates/
│   └── 🎨 index.html           # Interfaz web
├── 📖 guia_web_setup.md        # Guía detallada de configuración
└── 📄 README.md                # Este archivo
```

## ⚡ Inicio Rápido

### 1. Validar Configuración
```powershell
# Verificar que todo está configurado correctamente
python validar_setup.py
```

### 2. Configurar Credenciales GCP
- **Descargar**: Service Account JSON desde GCP Console
- **Guardar como**: `service-account.json` en el directorio del proyecto
- **Permisos requeridos**: Storage Object Admin en bucket xa-entel-data

### 3. Configuración Lista ✅
```json
// config_web.json ya está configurado correctamente
"project_id": "beside-352612"  // ✅ Actualizado
```

### 4. Ejecutar Aplicación
```powershell
# Método 1: Script automático (recomendado)
.\iniciar_web.bat

# Método 2: Manual
pip install -r requirements.txt
python app.py
```

### 5. Usar la Aplicación
1. **🔐 Conectar VPN** (manual con 2FA)
2. **🌐 Abrir**: http://127.0.0.1:5000
3. **🚀 Click**: "Iniciar Proceso de Transferencia"
4. **📊 Revisar**: Resultados en pantalla

## 🔧 Configuración Detallada

### Datos SFTP (Ya configurados)
- **Servidor**: 10.180.214.22:22
- **Usuario**: ftpuser
- **Contraseña**: PhTimwe.321
- **Archivos**: *.gz (comprimidos)

### Configuración GCP
```json
{
    "gcp": {
        "project_id": "beside-352612",          // ✅ Configurado correctamente
        "bucket_name": "xa-entel-data",         // ✅ Correcto
        "destination_folder": "Otros/"          // ✅ Correcto
    }
}
```

### Archivos Requeridos
- ✅ `config_web.json` - Configuración (incluido)
- ⚠️ `service-account.json` - Credenciales GCP (debes descargarlo)

## 📊 Características de la Aplicación

### Interfaz Web
- 🌐 **URL**: http://127.0.0.1:5000
- ⚠️ **Alertas**: Recordatorio de conexión VPN
- 📊 **Estado**: Verificación automática de conexiones
- 🚀 **Un click**: Botón para iniciar proceso completo

### Funcionalidades Automáticas
- ✅ **Validación inteligente**: Detecta última fecha en bucket
- ✅ **Descarga selectiva**: Solo archivos faltantes (desde última fecha hasta ayer)
- ✅ **Descompresión**: Automática .gz → .csv
- ✅ **Subida**: Directa a xa-entel-data/Otros
- ✅ **Limpieza**: Elimina archivos temporales
- ✅ **Logs detallados**: Para troubleshooting

### Manejo de Errores
- 🔍 **Validación previa**: Verifica VPN y credenciales
- 🔄 **Reintentos**: Para conexiones temporalmente fallidas
- 📝 **Logs específicos**: Identifica exactamente qué falló
- 🚨 **Alertas visuales**: En la interfaz web

## 📊 Monitoreo y Logs

### Ubicación de logs
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

## 🚨 Solución de Problemas

### Error: "Error conectando a GCP"
- ✅ Verifica que `service-account.json` existe
- ✅ Actualiza `project_id` en `config_web.json`
- ✅ Confirma permisos Storage Object Admin

### Error: "Error conectando a SFTP"
- ✅ **VPN debe estar conectada y autenticada**
- ✅ Verifica conectividad: `ping 10.180.214.22`
- ✅ Confirma que VPN permite tráfico al puerto 22

### Error: "No se pudo conectar al servidor"
- ✅ Ejecuta `python app.py` manualmente
- ✅ Verifica que puerto 5000 esté libre
- ✅ Confirma que Flask se inició correctamente

### Error: "403 Forbidden" en GCP
- ✅ Service account necesita rol `Storage Object Admin`
- ✅ Verifica que bucket `xa-entel-data` existe
- ✅ Confirma acceso a carpeta `Otros/`

## 📞 Información Específica del Proyecto

### Configuración SFTP (Confirmada)
- **IP**: 10.180.214.22
- **Puerto**: 22  
- **Usuario**: ftpuser
- **Contraseña**: PhTimwe.321
- **Archivos**: Formato .gz comprimidos

### Configuración GCP (Confirmada)
- **Bucket**: xa-entel-data
- **Carpeta**: Otros/
- **URL**: https://console.cloud.google.com/storage/browser/xa-entel-data/Otros

### Proceso Automático
- **Detección**: Última fecha de archivos en bucket
- **Período**: Desde última fecha hasta día anterior a ejecución
- **Formato**: Descomprime .gz → .csv antes de subir
- **Frecuencia**: Según necesidad (VPN manual)

## 🛠️ Comandos Útiles

```powershell
# Validar configuración completa
python validar_setup.py

# Iniciar aplicación web
.\iniciar_web.bat

# Verificar conexión GCP (manual)
python -c "from google.cloud import storage; print('GCP OK')"

# Verificar conectividad SFTP (con VPN)
ping 10.180.214.22

# Ver logs de aplicación en tiempo real
Get-Content transfer.log -Wait -Tail 10

# Acceder a la aplicación
start http://127.0.0.1:5000
```

---

🚀 **¿Listo para usar?** 
1. Ejecuta `python validar_setup.py` 
2. Conecta VPN manualmente
3. Ejecuta `.\iniciar_web.bat`
4. Abre http://127.0.0.1:5000
5. ¡Haz click en "Iniciar Proceso"!