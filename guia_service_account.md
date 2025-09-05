# 🔑 Guía Paso a Paso: Configuración Service Account GCP

## 📋 Resumen
Necesitas crear un Service Account en Google Cloud Platform para que la aplicación pueda acceder al bucket **xa-entel-data**.

## 🎯 Información de tu proyecto
- **Proyecto**: beside-352612
- **Bucket**: xa-entel-data
- **Carpeta destino**: Otros/

---

## 📝 PASO 1: Acceder a GCP Console

1. **Abrir GCP Console** en tu navegador
2. **Verificar proyecto**: Asegúrate de estar en el proyecto **beside-352612**
3. **Ir a Service Accounts**: Menú hamburguesa → IAM y administración → Cuentas de servicio

**URL directa**: https://console.cloud.google.com/iam-admin/serviceaccounts?project=beside-352612

---

## 📝 PASO 2: Crear Service Account

### 2.1 Hacer click en "CREAR CUENTA DE SERVICIO"

### 2.2 Completar información básica:
```
Nombre de la cuenta de servicio: sftp-gcp-transfer
ID de la cuenta de servicio: sftp-gcp-transfer (se genera automáticamente)
Descripción: Service account para transferencia automática SFTP → GCP
```

### 2.3 Hacer click en "CREAR Y CONTINUAR"

---

## 📝 PASO 3: Asignar Permisos

### 3.1 En "Otorgar acceso a esta cuenta de servicio al proyecto":

**Seleccionar rol**: `Storage Object Admin`

- En el campo "Seleccionar un rol"
- Buscar: "Storage Object Admin"
- Seleccionar: **Cloud Storage → Storage Object Admin**

### 3.2 Hacer click en "CONTINUAR"

### 3.3 En "Otorgar acceso a los usuarios a esta cuenta de servicio":
- **Dejar en blanco** (opcional)
- Hacer click en "LISTO"

---

## 📝 PASO 4: Descargar Credenciales JSON

### 4.1 En la lista de Service Accounts:
- Encontrar: **sftp-gcp-transfer**
- Hacer click en el **email** de la cuenta de servicio

### 4.2 Ir a la pestaña "CLAVES"

### 4.3 Crear nueva clave:
- Hacer click en "AGREGAR CLAVE"
- Seleccionar "Crear clave nueva"
- **Tipo**: JSON ✅
- Hacer click en "CREAR"

### 4.4 Guardar archivo:
- Se descargará un archivo JSON automáticamente
- **Renombrar a**: `service-account.json`
- **Mover a**: `C:\Users\XCAST\OneDrive\Escritorio\Reportes-SIM\`

---

## 📝 PASO 5: Verificar Permisos en el Bucket

### 5.1 Ir a Cloud Storage:
**URL**: https://console.cloud.google.com/storage/browser/xa-entel-data?project=beside-352612

### 5.2 Verificar acceso al bucket xa-entel-data:
- Debería aparecer el bucket en la lista
- Hacer click en **xa-entel-data**
- Verificar que existe la carpeta **Otros/**

### 5.3 Si hay problemas de permisos:
- En el bucket xa-entel-data → Pestaña "PERMISOS"
- Agregar principal: `sftp-gcp-transfer@beside-352612.iam.gserviceaccount.com`
- Rol: **Storage Object Admin**

---

## ✅ PASO 6: Verificar Configuración

Una vez descargado el `service-account.json`:

```powershell
# Ir al directorio del proyecto
cd "C:\Users\XCAST\OneDrive\Escritorio\Reportes-SIM"

# Verificar que el archivo existe
dir service-account.json

# Ejecutar validación completa
python validar_setup.py
```

---

## 🚨 Solución de Problemas

### Error: "Bucket no encontrado"
- Verificar que estás en el proyecto correcto: **beside-352612**
- Confirmar que el bucket **xa-entel-data** existe

### Error: "403 Forbidden"
- El Service Account necesita permisos en el bucket específico
- Verificar rol **Storage Object Admin**

### Error: "Credenciales inválidas"
- Verificar que el archivo JSON se descargó correctamente
- Confirmar que se llama exactamente `service-account.json`

---

## 📋 Checklist Final

- [ ] Service Account creado: `sftp-gcp-transfer`
- [ ] Rol asignado: `Storage Object Admin`
- [ ] Archivo descargado: `service-account.json`
- [ ] Archivo en ubicación correcta: `C:\Users\XCAST\OneDrive\Escritorio\Reportes-SIM\`
- [ ] Validación exitosa: `python validar_setup.py`

---

## 🎉 ¡Listo para usar!

Una vez completados todos los pasos:

```powershell
# Ejecutar aplicación
.\iniciar_web.bat

# Abrir en navegador
start http://127.0.0.1:5000
```

**¡Ya podrás transferir archivos con un solo click!** 🚀