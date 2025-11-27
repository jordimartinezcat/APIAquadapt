-- =====================================================
-- Script SQL para crear tablas de integración con updateDate
-- AquaAdvanced API -> PostgreSQL Data Lake
-- Versión DETAILED con fechas de actualización
-- =====================================================

-- =====================================================
-- 1. TABLA DE MAPEO (ga_integration) - Sin cambios
-- =====================================================

CREATE SCHEMA IF NOT EXISTS ga_integration;

CREATE TABLE IF NOT EXISTS ga_integration.ite_aqapi_tag (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    api_id VARCHAR NOT NULL,
    tag VARCHAR NULL,
    tag_cabal VARCHAR NULL,
    tipus VARCHAR(50) NOT NULL CHECK (tipus IN ('bomba', 'valvula'))
);

-- Comentarios
COMMENT ON TABLE ga_integration.ite_aqapi_tag IS 'Mapeo entre IDs de AquaAdvanced API y tags internos';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.id IS 'ID secuencial del registro';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.api_id IS 'ID del dispositivo en AquaAdvanced API (UUID)';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.tag IS 'ID del tag para on/off';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.tag_cabal IS 'ID del tag para caudal (válvulas)';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.tipus IS 'Tipo de dispositivo (bomba o valvula)';


-- =====================================================
-- 2. TABLA DE DATOS DETALLADA (ga_landing)
-- Incluye updateDate para on/off y caudal
-- =====================================================

CREATE SCHEMA IF NOT EXISTS ga_landing;

CREATE TABLE IF NOT EXISTS ga_landing.ite_aqapi_fullhist (
    fecha TIMESTAMP NOT NULL,
    id VARCHAR(255) NOT NULL,
    valor_on_off INTEGER NULL,
    valor_caudal FLOAT8 NULL,
    update_date_on_off TIMESTAMP NULL,
    update_date_caudal TIMESTAMP NULL,
    PRIMARY KEY (fecha, id)
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_fullhist_fecha ON ga_landing.ite_aqapi_fullhist(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_fullhist_id ON ga_landing.ite_aqapi_fullhist(id);
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_fullhist_update_onoff ON ga_landing.ite_aqapi_fullhist(update_date_on_off DESC);
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_fullhist_update_caudal ON ga_landing.ite_aqapi_fullhist(update_date_caudal DESC);

-- Comentarios
COMMENT ON TABLE ga_landing.ite_aqapi_fullhist IS 'Datos de programación desde AquaAdvanced con fechas de actualización (on/off y caudal)';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.fecha IS 'Fecha y hora del dato (timestamp del registro)';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.id IS 'ID del registro (referencia a ite_aqapi_tag.id)';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.valor_on_off IS 'Valor on/off (0/1)';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.valor_caudal IS 'Valor de caudal programado (l/s o m3/h)';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.update_date_on_off IS 'Fecha de última actualización del valor on/off';
COMMENT ON COLUMN ga_landing.ite_aqapi_fullhist.update_date_caudal IS 'Fecha de última actualización del valor de caudal';


-- =====================================================
-- 3. VISTA para consultas rápidas
-- =====================================================

CREATE OR REPLACE VIEW ga_landing.v_aqapi_fullhist_con_ids AS
SELECT 
    f.fecha,
    f.id,
    f.valor_on_off,
    f.valor_caudal,
    f.update_date_on_off,
    f.update_date_caudal,
    m.api_id,
    m.tag,
    m.tag_cabal,
    m.tipus
FROM 
    ga_landing.ite_aqapi_fullhist f
    LEFT JOIN ga_integration.ite_aqapi_tag m ON f.id::bigint = m.id
ORDER BY 
    f.fecha DESC;

COMMENT ON VIEW ga_landing.v_aqapi_fullhist_con_ids IS 'Vista con datos históricos completos incluyendo API IDs, tags y fechas de actualización';


-- =====================================================
-- 4. CONSULTAS ÚTILES
-- =====================================================

-- Ver todos los mapeos
-- SELECT * FROM ga_integration.ite_aqapi_tag ORDER BY api_id;

-- Ver últimos datos insertados
-- SELECT * FROM ga_landing.v_aqapi_fullhist_con_ids LIMIT 100;

-- Contar registros por dispositivo
-- SELECT id, COUNT(*) as total_registros 
-- FROM ga_landing.ite_aqapi_fullhist 
-- GROUP BY id 
-- ORDER BY total_registros DESC;

-- Ver datos con información de actualización
-- SELECT fecha, id, valor_on_off, valor_caudal,
--        update_date_on_off, update_date_caudal,
--        (update_date_on_off - fecha) as delay_on_off,
--        (update_date_caudal - fecha) as delay_caudal
-- FROM ga_landing.ite_aqapi_fullhist
-- ORDER BY fecha DESC
-- LIMIT 100;

-- Ver registros actualizados recientemente
-- SELECT * FROM ga_landing.v_aqapi_fullhist_con_ids 
-- WHERE update_date_on_off >= NOW() - INTERVAL '1 hour'
--    OR update_date_caudal >= NOW() - INTERVAL '1 hour'
-- ORDER BY GREATEST(update_date_on_off, update_date_caudal) DESC;

-- Comparar update_date entre on/off y caudal
-- SELECT 
--     COUNT(*) FILTER (WHERE update_date_on_off IS NOT NULL) as con_update_onoff,
--     COUNT(*) FILTER (WHERE update_date_caudal IS NOT NULL) as con_update_caudal,
--     COUNT(*) FILTER (WHERE update_date_on_off IS NOT NULL AND update_date_caudal IS NOT NULL) as con_ambos_updates
-- FROM ga_landing.ite_aqapi_fullhist;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
