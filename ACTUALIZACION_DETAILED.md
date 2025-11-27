# Actualización: Endpoints Detailed y Caudal para Bombas

## 📋 Resumen de Cambios

Se han realizado las siguientes modificaciones al sistema para:

1. ✅ **Consultar caudal (flowschedule) también para bombas**
2. ✅ **Usar endpoints `/detailed/` por defecto** para obtener `updateDate`
3. ✅ **Crear nueva tabla PostgreSQL** con columnas para fechas de actualización

---

## 🔧 Modificaciones Realizadas

### 1. API Client (`aquadapt_api_client_oficial_v2.py`)

#### ✨ Nuevo método: `get_bomba_flowschedule()`

```python
def get_bomba_flowschedule(
    self, bomba_id: str, start_time: str = None, end_time: str = None, detailed: bool = True
) -> Any:
    """
    Obtener programación de caudal (flowschedule) de una bomba

    Endpoint: physicalPumps/{bomba_id}/flowschedule/detailed/
    """
```

#### 🔄 Métodos actualizados a `detailed=True` por defecto:

- `get_bomba_onoffschedule()` → usa `/onoffschedule/detailed/`
- `get_valve_onoffschedule()` → usa `/onoffschedule/detailed/`
- `get_valve_scheduledflow()` → usa `/scheduledflow/detailed/`

**Beneficio**: Ahora todos los endpoints devuelven `updateDate` además de `value` y `timestamp`

---

### 2. Script de Sincronización (`sync_scheduledflow_to_db.py`)

#### 🆕 Constante actualizada:

```python
TABLE_TARGET = "ite_aqapi_hist_detailed"  # Nueva tabla con updateDates
```

#### 🔄 Método `consultar_scheduledflow()` actualizado:

- Ahora acepta parámetro `device_tipo` ('bomba' o 'valvula')
- Consulta `get_bomba_flowschedule()` para bombas
- Consulta `get_valve_scheduledflow()` para válvulas

#### 🔄 Método `transformar_datos()` actualizado:

- **Nueva columna**: `update_date_on_off`
- Extrae `updateDate` del response de la API cuando está disponible

#### 🔄 Método `transformar_datos_caudal()` actualizado:

- **Nueva columna**: `update_date_caudal`
- Extrae `updateDate` del response de flowschedule/scheduledflow

#### 🔄 Método `insertar_datos()` actualizado:

- Inserta 6 columnas:
  - `fecha`
  - `id`
  - `valor_on_off`
  - `valor_caudal`
  - **`update_date_on_off`** ← NUEVO
  - **`update_date_caudal`** ← NUEVO
- Actualiza ON CONFLICT para incluir update_dates

#### ⚡ Método `procesar_dispositivos()` actualizado:

**Para BOMBAS** (cambio principal):

```python
# Consultar onoffschedule
datos_raw_onoff = self.consultar_onoffschedule(...)
df_onoff = self.transformar_datos(...)

# NUEVO: Para bombas, consultar también flowschedule (caudal)
datos_raw_caudal = self.consultar_scheduledflow(..., "bomba", ...)
df_caudal = self.transformar_datos_caudal(...)

# Merge on/off y caudal
df_device = pd.merge(df_onoff, df_caudal, on=["fecha", "id"], how="outer")
```

**Para VÁLVULAS** (sin cambios en lógica, solo se agregó device_tipo):

- Sigue consultando onoffschedule + scheduledflow
- Merge de ambos dataframes

---

### 3. Nueva Tabla PostgreSQL

#### 📄 Archivo: `setup_database_tables_detailed.sql`

```sql
CREATE TABLE IF NOT EXISTS ga_landing.ite_aqapi_hist_detailed (
    fecha TIMESTAMP NOT NULL,
    id VARCHAR(255) NOT NULL,
    valor_on_off INTEGER NULL,
    valor_caudal FLOAT8 NULL,
    update_date_on_off TIMESTAMP NULL,    -- ← NUEVO
    update_date_caudal TIMESTAMP NULL,    -- ← NUEVO
    PRIMARY KEY (fecha, id)
);
```

#### 📊 Índices creados:

```sql
CREATE INDEX idx_ite_aqapi_hist_detailed_fecha ON ite_aqapi_hist_detailed(fecha DESC);
CREATE INDEX idx_ite_aqapi_hist_detailed_id ON ite_aqapi_hist_detailed(id);
CREATE INDEX idx_ite_aqapi_hist_detailed_update_onoff ON ite_aqapi_hist_detailed(update_date_on_off DESC);
CREATE INDEX idx_ite_aqapi_hist_detailed_update_caudal ON ite_aqapi_hist_detailed(update_date_caudal DESC);
```

#### 👁️ Vista actualizada:

```sql
CREATE OR REPLACE VIEW ga_landing.v_aqapi_hist_detailed_con_ids AS
SELECT
    f.fecha,
    f.id,
    f.valor_on_off,
    f.valor_caudal,
    f.update_date_on_off,      -- ← NUEVO
    f.update_date_caudal,      -- ← NUEVO
    m.api_id,
    m.tag,
    m.tag_cabal,
    m.tipus
FROM
    ga_landing.ite_aqapi_hist_detailed f
    LEFT JOIN ga_integration.ite_aqapi_tag m ON f.id::bigint = m.id
ORDER BY
    f.fecha DESC;
```

---

## 📊 Comparación Antes/Después

### Antes:

| Dispositivo | Endpoint onoffschedule              | Endpoint flowschedule/scheduledflow | updateDate |
| ----------- | ----------------------------------- | ----------------------------------- | ---------- |
| Bomba       | ✅ physicalPumps/{id}/onoffschedule | ❌ No se consultaba                 | ❌ No      |
| Válvula     | ✅ valves/{id}/onoffschedule        | ✅ valves/{id}/scheduledflow        | ❌ No      |

**Tabla**: `ite_aqapi_hist` con 4 columnas (fecha, id, valor_on_off, valor_caudal)

### Después:

| Dispositivo | Endpoint onoffschedule                            | Endpoint flowschedule/scheduledflow              | updateDate |
| ----------- | ------------------------------------------------- | ------------------------------------------------ | ---------- |
| Bomba       | ✅ physicalPumps/{id}/onoffschedule/**detailed/** | ✅ physicalPumps/{id}/flowschedule/**detailed/** | ✅ Sí      |
| Válvula     | ✅ valves/{id}/onoffschedule/**detailed/**        | ✅ valves/{id}/scheduledflow/**detailed/**       | ✅ Sí      |

**Tabla**: `ite_aqapi_hist_detailed` con **6 columnas** (fecha, id, valor_on_off, valor_caudal, update_date_on_off, update_date_caudal)

---

## 🚀 Pasos para Implementar

### 1. Crear la nueva tabla en PostgreSQL:

```bash
psql -h 40.85.79.213 -p 5432 -U ga_nifisagecad -d goaigua_data -f setup_database_tables_detailed.sql
```

### 2. Otorgar permisos:

```sql
GRANT SELECT ON ga_integration.ite_aqapi_tag TO ga_nifisagecad;
GRANT SELECT, INSERT, UPDATE ON ga_landing.ite_aqapi_hist_detailed TO ga_nifisagecad;
```

### 3. Ejecutar script actualizado:

```bash
python sync_scheduledflow_to_db.py
```

---

## 📈 Resultados Esperados

Después de la ejecución:

- **Bombas**: ~6,555 registros (69 × 95) con **AMBOS** `valor_on_off` Y `valor_caudal`
- **Válvulas**: ~9,690 registros (102 × 95) con **AMBOS** `valor_on_off` Y `valor_caudal`
- **Total**: ~16,245 registros

### Datos adicionales capturados:

- ✅ `update_date_on_off`: Fecha de última modificación del estado on/off
- ✅ `update_date_caudal`: Fecha de última modificación del caudal programado

---

## 🔍 Consultas Útiles

### Ver registros con update_dates:

```sql
SELECT
    fecha, id, valor_on_off, valor_caudal,
    update_date_on_off, update_date_caudal,
    (update_date_on_off - fecha) as delay_on_off,
    (update_date_caudal - fecha) as delay_caudal
FROM ga_landing.ite_aqapi_hist_detailed
ORDER BY fecha DESC
LIMIT 100;
```

### Ver actualizaciones recientes:

```sql
SELECT *
FROM ga_landing.v_aqapi_hist_detailed_con_ids
WHERE update_date_on_off >= NOW() - INTERVAL '1 hour'
   OR update_date_caudal >= NOW() - INTERVAL '1 hour'
ORDER BY GREATEST(update_date_on_off, update_date_caudal) DESC;
```

### Estadísticas de update_dates:

```sql
SELECT
    COUNT(*) FILTER (WHERE update_date_on_off IS NOT NULL) as con_update_onoff,
    COUNT(*) FILTER (WHERE update_date_caudal IS NOT NULL) as con_update_caudal,
    COUNT(*) FILTER (WHERE update_date_on_off IS NOT NULL AND update_date_caudal IS NOT NULL) as con_ambos_updates
FROM ga_landing.ite_aqapi_hist_detailed;
```

---

## ✅ Verificación

Para verificar que todo funciona correctamente:

1. ✅ API client tiene método `get_bomba_flowschedule()`
2. ✅ Todos los métodos usan `detailed=True` por defecto
3. ✅ Script consulta flowschedule para bombas Y válvulas
4. ✅ Transformación extrae `updateDate` de respuestas
5. ✅ Tabla `ite_aqapi_hist_detailed` creada con 6 columnas
6. ✅ INSERT maneja las 6 columnas correctamente
7. ✅ Vista incluye columnas de update_date

---

## 📝 Notas Importantes

⚠️ **Tabla nueva**: El script ahora usa `ite_aqapi_hist_detailed` en lugar de `ite_aqapi_hist`

⚠️ **Compatibilidad**: La tabla antigua `ite_aqapi_hist` sigue existiendo, se puede mantener para histórico

⚠️ **Performance**: Ahora se hacen **2× consultas** por cada dispositivo (onoffschedule + flowschedule), el tiempo de ejecución puede aumentar

⚠️ **Endpoints detailed**: Requieren `/detailed/` al final de la URL (ya está implementado)

---

## 🎯 Beneficios

1. **✅ Datos completos de bombas**: Ahora se captura el caudal programado de las bombas
2. **✅ Trazabilidad**: `updateDate` permite saber cuándo se modificó cada valor
3. **✅ Auditoría**: Se puede detectar cuándo hubo cambios en la programación
4. **✅ Análisis temporal**: Se puede analizar el delay entre `fecha` y `updateDate`
5. **✅ Consistencia**: Bombas y válvulas ahora tienen la misma estructura de datos
