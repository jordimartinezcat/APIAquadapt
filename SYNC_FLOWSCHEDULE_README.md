# 🔄 Sincronización FlowSchedule a PostgreSQL

Script automatizado para consultar datos de `flowschedule` desde la API de AquaAdvanced y almacenarlos en PostgreSQL Data Lake.

Diseñado para ejecución periódica desde **Apache NiFi** o cualquier programador de tareas.

---

## 📋 Descripción

Este script realiza las siguientes operaciones:

1. **Obtiene mapeo de tags** desde tabla `ga_integration.ite_aqapi_tag`
2. **Consulta API AquaAdvanced** para obtener flowschedule de:
   - Bombas (physicalPumps)
   - Válvulas (valves)
3. **Transforma datos** al formato requerido (fecha, idtag, valor)
4. **Inserta en PostgreSQL** tabla `ga_datalake.aquaadvanced_flowschedule`

---

## 🗄️ Estructura de Base de Datos

### Tabla de Mapeo: `ga_integration.ite_aqapi_tag`

Relaciona IDs de la API con tags internos.

```sql
CREATE TABLE ga_integration.ite_aqapi_tag (
    id SERIAL PRIMARY KEY,
    api_id VARCHAR(255) NOT NULL UNIQUE,      -- ID de AquaAdvanced API
    idtag VARCHAR(255) NOT NULL UNIQUE,       -- Tag interno
    tipo VARCHAR(50) NOT NULL,                -- 'bomba' o 'valvula'
    nombre VARCHAR(255),                      -- Nombre descriptivo
    activo BOOLEAN DEFAULT true               -- Si está activo para sync
);
```

**Ejemplo de datos:**

```sql
INSERT INTO ga_integration.ite_aqapi_tag (api_id, idtag, tipo, nombre)
VALUES
    ('040b3d5d-a68a-dc52-0623-5d2f6fcd2682', 'TAG_EB3_G4_FLOW', 'bomba', 'EB3 G4'),
    ('uuid-valvula-123', 'TAG_VALVE_01_FLOW', 'valvula', 'Válvula Principal');
```

### Tabla de Datos: `ga_datalake.aquaadvanced_flowschedule`

Almacena los datos históricos de flowschedule.

```sql
CREATE TABLE ga_datalake.aquaadvanced_flowschedule (
    id BIGSERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL,                 -- Fecha/hora del dato
    idtag VARCHAR(255) NOT NULL,              -- Tag (FK a ite_aqapi_tag)
    valor DOUBLE PRECISION,                   -- Valor del flujo
    CONSTRAINT uk_fecha_idtag UNIQUE (fecha, idtag)
);
```

---

## 🚀 Instalación

### 1. Crear tablas en PostgreSQL

```bash
psql -h 40.85.79.213 -U ga_nifisagecad -d goaigua_data -f setup_database_tables.sql
```

O ejecutar manualmente el contenido de `setup_database_tables.sql`.

### 2. Configurar mapeo de tags

Insertar registros en `ga_integration.ite_aqapi_tag` con tus dispositivos:

```sql
-- Obtener IDs de dispositivos de la API
SELECT id, name FROM bombas_en_sistema;

-- Insertar mapeo
INSERT INTO ga_integration.ite_aqapi_tag (api_id, idtag, tipo, nombre)
VALUES ('API-ID-AQUI', 'TU-TAG-AQUI', 'bomba', 'Nombre Bomba');
```

### 3. Instalar dependencias Python

```bash
pip install pandas psycopg2 requests
```

---

## ⚙️ Configuración

### Variables de entorno (opcional)

```bash
export TIME_WINDOW_HOURS=24  # Ventana temporal en horas (por defecto 24)
```

### En el script

Editar `sync_scheduledflow_to_db.py`:

```python
# Configuración
TIME_WINDOW_HOURS = 24  # Últimas 24 horas
SCHEMA_INTEGRATION = 'ga_integration'
SCHEMA_DATALAKE = 'ga_datalake'
TABLE_MAPPING = 'ite_aqapi_tag'
TABLE_TARGET = 'aquaadvanced_flowschedule'
```

---

## 📊 Uso

### Ejecución Manual

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Ejecutar script
python sync_scheduledflow_to_db.py
```

### Ejecución desde Apache NiFi

**Procesador:** ExecuteStreamCommand o ExecuteScript

**Configuración:**

```
Command: python
Command Arguments: /ruta/completa/sync_scheduledflow_to_db.py
Working Directory: /ruta/al/proyecto/APIAquadapt
```

**Scheduling:**

```
Run Schedule: 0 0 * * * *  # Cada hora
Concurrent Tasks: 1
Run Duration: 0 ms
```

**Variables de entorno en NiFi:**

```
PYTHONPATH=/ruta/al/proyecto/APIAquadapt:/ruta/CAT_Conexions/src
```

---

## 📝 Logs

El script genera logs en:

- **Consola**: Output estándar
- **Archivo**: `sync_scheduledflow.log` en el directorio del script

### Formato de logs

```
2025-11-25 10:30:00 - INFO - 🚀 INICIANDO SINCRONIZACIÓN FLOWSCHEDULE
2025-11-25 10:30:01 - INFO - ✅ Conectado a PostgreSQL Data Lake
2025-11-25 10:30:02 - INFO - 📊 Obteniendo mapeo de tags desde ga_integration.ite_aqapi_tag
2025-11-25 10:30:02 - INFO - ✅ Mapeo obtenido: 85 registros
2025-11-25 10:30:03 - INFO -    📡 Consultando flowschedule de: EB3 G4
2025-11-25 10:30:04 - INFO -       ✅ 120 registros obtenidos
2025-11-25 10:30:10 - INFO - 💾 Insertando 1250 registros en ga_datalake.aquaadvanced_flowschedule...
2025-11-25 10:30:15 - INFO - ✅ PROCESO COMPLETADO EXITOSAMENTE
```

---

## 🔍 Monitoreo

### Verificar última ejecución

```sql
-- Ver últimos datos insertados
SELECT MAX(fecha_insercion) as ultima_insercion,
       COUNT(*) as total_registros
FROM ga_datalake.aquaadvanced_flowschedule;
```

### Ver registros por dispositivo

```sql
SELECT
    m.nombre,
    m.tipo,
    COUNT(*) as total_registros,
    MAX(f.fecha) as ultima_fecha,
    MIN(f.fecha) as primera_fecha
FROM ga_datalake.aquaadvanced_flowschedule f
JOIN ga_integration.ite_aqapi_tag m ON f.idtag = m.idtag
GROUP BY m.nombre, m.tipo
ORDER BY total_registros DESC;
```

### Verificar integridad

```sql
-- Dispositivos sin datos
SELECT m.nombre, m.tipo, m.idtag
FROM ga_integration.ite_aqapi_tag m
LEFT JOIN ga_datalake.aquaadvanced_flowschedule f ON m.idtag = f.idtag
WHERE m.activo = true AND f.id IS NULL;
```

---

## ⚠️ Manejo de Errores

El script maneja automáticamente:

- ❌ **Sin conexión a API**: Log error y exit code 1
- ❌ **Sin conexión a DB**: Log error y exit code 1
- ⚠️ **Dispositivo sin datos**: Log warning, continúa
- ⚠️ **Endpoint no disponible**: Log warning, continúa
- ✅ **Duplicados**: Constraint UNIQUE evita duplicados

### Códigos de salida

- `0`: Ejecución exitosa
- `1`: Error crítico (revisar logs)

---

## 🔧 Troubleshooting

### Error: "CAT_Conexions no disponible"

```bash
# Verificar submodule
git submodule update --init --recursive

# Verificar path
export PYTHONPATH="${PYTHONPATH}:/ruta/al/proyecto/CAT_Conexions/src"
```

### Error: "No se pudo obtener mapeo"

```sql
-- Verificar tabla existe
SELECT * FROM ga_integration.ite_aqapi_tag LIMIT 5;

-- Verificar registros activos
SELECT COUNT(*) FROM ga_integration.ite_aqapi_tag WHERE activo = true;
```

### Sin datos obtenidos

1. Verificar ventana temporal (ampliar `TIME_WINDOW_HOURS`)
2. Verificar IDs en mapeo coinciden con API
3. Consultar manualmente endpoint flowschedule

---

## 📈 Optimizaciones

### Para grandes volúmenes de datos

1. **Inserción por lotes** (batch inserts)
2. **Particionamiento** de tabla por fechas
3. **Índices adicionales** según patrones de consulta
4. **Limpieza periódica** de datos antiguos

### Script de limpieza (opcional)

```sql
-- Eliminar datos antiguos (> 1 año)
DELETE FROM ga_datalake.aquaadvanced_flowschedule
WHERE fecha < NOW() - INTERVAL '1 year';
```

---

## 📚 Referencias

- [AquaAdvanced API Documentation](https://aquadvanced.ccaait.local/publication)
- [CAT_Conexions Repository](https://github.com/jordimartinezcat/CAT_Conexions)
- [Apache NiFi ExecuteStreamCommand](https://nifi.apache.org/docs/nifi-docs/components/org.apache.nifi/nifi-standard-nar/1.15.0/org.apache.nifi.processors.standard.ExecuteStreamCommand/)

---

## 🤝 Soporte

Para problemas o mejoras:

1. Revisar logs en `sync_scheduledflow.log`
2. Verificar configuración de tablas y mapeo
3. Contactar equipo de desarrollo

---

**Última actualización:** 2025-11-25
