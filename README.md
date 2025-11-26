# 🚀 AquaAdvanced API Client - FUNCIONANDO ✅

Cliente Python para acceder a la API de AquaAdvanced y obtener datos de bombas y equipos de monitoreo.

## 📋 **ESTADO: COMPLETADO Y FUNCIONANDO CORRECTAMENTE**

- ✅ **Fecha**: 24 de Octubre, 2025
- ✅ **Versión**: 2.0 (Corregida)
- ✅ **Estado**: Listo para Producción
- ✅ **Pruebas**: Todas las funcionalidades verificadas
- ✅ **Formato de Fechas**: Implementado formato API `2025-10-22T00%3A00%3A00Z`

## 📁 Estructura del Proyecto

### Archivos Principales

- **`aquadapt_api_client_oficial_v2.py`** - Cliente principal de la API (versión final)
- **`config.py`** - Configuración centralizada (API key, endpoints, etc.)
- **`main.py`** - Interfaz interactiva para consultas (solo JSON)
- **`main_with_db.py`** - 🆕 Interfaz con integración PostgreSQL/IoT Core
- **`ejemplos_uso_corregido.py`** - Ejemplos interactivos de uso
- **`demostracion_final.py`** - Script de demostración completa

### Subproyectos

- **`CAT_Conexions/`** - 🆕 Módulo de conexiones con bases de datos
  - PostgreSQL Data Lake
  - Ver [CAT_Conexions README](CAT_Conexions/README.md) para más detalles

### Archivos de Datos

- **`aquadapt BMB Id.json`** - Lista de bombas con IDs y nombres
- **`aquadapt_ids_names.csv`** - Datos en formato CSV
- **`aquadapt BMB Id.json.backup_20251023_084622`** - Respaldo del archivo original

### Utilidades

- **`fix_json_bom.py`** - Script para corregir codificación BOM UTF-8 en archivos JSON
- **`extract_ids_names.py`** - Extractor de IDs y nombres de bombas

### Versiones Anteriores (Referencia)

- **`aquadapt_api_client_oficial.py`** - Versión anterior del cliente
- **`aquadapt_api_client.py`** - Primera versión del cliente
- **`ejemplos_uso_oficial.py`** - Versión anterior de ejemplos
- **`ejemplos_uso_fixed.py`** - Versión corregida de ejemplos
- **`ejemplos_uso.py`** - Primera versión de ejemplos

## 🚀 Uso Rápido

1. **Configuración**: Edita `config.py` con tu API key si es necesario
2. **Consulta simple**: `python main.py`
3. **Con integración DB**: `python main_with_db.py`
4. **Ejemplos avanzados**: `python ejemplos_uso_corregido.py`
5. **Demostración completa**: `python demostracion_final.py`

## ✅ Características

- ✅ Autenticación con API Key
- ✅ Acceso a 73 bombas del sistema
- ✅ 16 endpoints de datos por bomba
- ✅ Manejo automático de codificación BOM UTF-8
- ✅ Sistema de reintentos y manejo de errores
- ✅ Soporte para datos temporales con rangos de fecha
- ✅ Fallback a archivo local si la API no responde

## 📊 API Endpoints Disponibles

Por cada bomba se pueden consultar:

- Status (estado actual)
- Raw Power (potencia)
- Speed (velocidad)
- Faults (fallos)
- In Service (en servicio)
- AAE Control (control automático)
- On/Off Schedule (programación encendido/apagado)
- Flow Schedule (programación de caudal)

Cada endpoint tiene versión normal y detallada.

## 🔧 Configuración

El archivo `config.py` contiene:

- URL base de la API
- API Key de autenticación
- Configuración de SSL y timeouts
- Endpoints disponibles
- Opciones de logging

## � Formato de Fechas para la API

La API de AquaAdvanced requiere fechas en formato específico: `2025-10-22T00%3A00%3A00Z`

### Características:

- **Base ISO 8601**: `YYYY-MM-DDTHH:MM:SSZ`
- **URL Encoding**: Los dos puntos (`:`) se codifican como `%3A`
- **UTC Timezone**: Debe terminar con `Z`
- **Conversión Automática**: El cliente convierte automáticamente fechas estándar

### Ejemplos:

```
2025-10-22T00:00:00        → 2025-10-22T00%3A00%3A00Z
2025-10-22T14:30:45.123456 → 2025-10-22T14%3A30%3A45Z
```

📖 **Ver documentación completa**: [FECHA_API_FORMAT.md](FECHA_API_FORMAT.md)

## �📝 Notas

- Las respuestas vacías son normales cuando no hay datos históricos
- Todos los endpoints responden correctamente (HTTP 200)
- Los enlaces href de la API se utilizan dinámicamente
- El cliente maneja automáticamente la codificación BOM UTF-8
- **Formato de fechas implementado correctamente** según especificaciones de la API

## 🔗 Integración con CAT_Conexions

El proyecto incluye integración con **CAT_Conexions** para ampliar capacidades:

### Características adicionales:

- ✅ **Almacenamiento en PostgreSQL Data Lake** - Guarda datos históricos de bombas
- ✅ **Consultas avanzadas** - Combina datos de múltiples fuentes
- ✅ **Análisis histórico** - Genera reportes desde base de datos

### Uso de integración:

```python
# Importar módulo de conexiones
from CAT_Conexions.src.conexions import pgDataLake

# Conectar a Data Lake
dl = pgDataLake()
dl.connect()

# Guardar datos de API en PostgreSQL
datos_bomba = client.get_bomba_status(bomba_id, start, end)
dl.insert_data_batch(df_datos, 'aquaadvanced_status')
```

### Actualizar submodule:

```bash
git submodule update --remote CAT_Conexions
```

## 🎯 Proyecto Completado

Este cliente cumple completamente con el objetivo de consultar la API de AquaAdvanced para obtener datos JSON de bombas y equipos de monitoreo, con capacidades extendidas de almacenamiento y análisis mediante CAT_Conexions.

---

_Desarrollado para acceso a la API de AquaAdvanced en https://aquadvanced.ccaait.local/publication_
