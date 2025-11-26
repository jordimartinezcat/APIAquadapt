-- =====================================================
-- Script SQL para crear tablas de integración
-- AquaAdvanced API -> PostgreSQL Data Lake
-- =====================================================

-- =====================================================
-- 1. TABLA DE MAPEO (ga_integration)
-- Tabla intermedia para mapear IDs de API con IDTags
-- =====================================================

CREATE SCHEMA IF NOT EXISTS ga_integration;

CREATE TABLE IF NOT EXISTS ga_integration.ite_aqapi_tag (
    api_id VARCHAR(255) NOT NULL PRIMARY KEY,
    idtag VARCHAR(255) NOT NULL UNIQUE,
    tipus VARCHAR(50) NOT NULL CHECK (tipus IN ('bomba', 'valvula'))
);

-- Índice para búsqueda inversa por idtag
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_tag_idtag ON ga_integration.ite_aqapi_tag(idtag);

-- Comentarios
COMMENT ON TABLE ga_integration.ite_aqapi_tag IS 'Mapeo entre IDs de AquaAdvanced API y tags internos';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.api_id IS 'ID del dispositivo en AquaAdvanced API (UUID)';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.idtag IS 'ID del tag interno para Data Lake';


-- =====================================================
-- 2. TABLA DE DATOS (ga_datalake)
-- Tabla destino para almacenar datos de flowschedule
-- =====================================================

CREATE SCHEMA IF NOT EXISTS ga_landing;

CREATE TABLE IF NOT EXISTS ga_landing.ite_aqapi_hist (
    fecha TIMESTAMP NOT NULL,
    idtag VARCHAR(255) NOT NULL,
    valor INTEGER,
    PRIMARY KEY (fecha, idtag)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_hist_fecha ON ga_landing.ite_aqapi_hist(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_hist_idtag ON ga_landing.ite_aqapi_hist(idtag);

-- Comentarios
COMMENT ON TABLE ga_landing.ite_aqapi_hist IS 'Datos de programación de flujo desde AquaAdvanced';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.fecha IS 'Fecha y hora del dato';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.idtag IS 'ID del tag (referencia a ite_aqapi_tag)';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.valor IS 'Valor del flujo programado (entero)';


-- =====================================================
-- 3. DATOS DE EJEMPLO para tabla de mapeo
-- Insertar registros de ejemplo (ajustar con datos reales)
-- =====================================================

-- EJEMPLO: Mapeo de bombas
-- Reemplazar con IDs reales de tu sistema

/*
-- EJEMPLO: Mapeo de bombas (usar endpoint physicalPumps)
INSERT INTO ga_integration.ite_aqapi_tag (api_id, idtag, tipus)
VALUES 
    ('040b3d5d-a68a-dc52-0623-5d2f6fcd2682', '103905', 'bomba'),
    ('otro-uuid-bomba', 'TAG_EB1_G1_FLOW', 'bomba')
ON CONFLICT (api_id) DO UPDATE SET idtag = EXCLUDED.idtag, tipus = EXCLUDED.tipus;

-- EJEMPLO: Mapeo de válvulas (usar endpoint valves)
INSERT INTO ga_integration.ite_aqapi_tag (api_id, idtag, tipus)
VALUES 
    ('uuid-valvula-1', 'TAG_VALVE_01_FLOW', 'valvula'),
    ('uuid-valvula-2', 'TAG_VALVE_02_FLOW', 'valvula')
ON CONFLICT (api_id) DO UPDATE SET idtag = EXCLUDED.idtag, tipus = EXCLUDED.tipus;
*/


-- =====================================================
-- 4. VISTA para consultas rápidas
-- =====================================================

CREATE OR REPLACE VIEW ga_landing.v_aqapi_hist_con_ids AS
SELECT 
    f.fecha,
    f.idtag,
    f.valor,
    m.api_id
FROM 
    ga_landing.ite_aqapi_hist f
    LEFT JOIN ga_integration.ite_aqapi_tag m ON f.idtag = m.idtag
ORDER BY 
    f.fecha DESC;

COMMENT ON VIEW ga_landing.v_aqapi_hist_con_ids IS 'Vista con datos históricos incluyendo API IDs';


-- =====================================================
-- 5. CONSULTAS ÚTILES
-- =====================================================

-- Ver todos los mapeos
-- SELECT * FROM ga_integration.ite_aqapi_tag ORDER BY api_id;

-- Ver últimos datos insertados
-- SELECT * FROM ga_landing.v_aqapi_hist_con_ids LIMIT 100;

-- Contar registros por dispositivo
-- SELECT idtag, COUNT(*) as total_registros 
-- FROM ga_landing.ite_aqapi_hist 
-- GROUP BY idtag 
-- ORDER BY total_registros DESC;

-- Ver datos de última hora
-- SELECT * FROM ga_landing.v_aqapi_hist_con_ids 
-- WHERE fecha >= NOW() - INTERVAL '1 hour' 
-- ORDER BY fecha DESC;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
