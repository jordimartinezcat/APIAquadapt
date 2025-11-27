-- =====================================================
-- Script de Migración para Actualizar Esquema de Tablas
-- Versión 2: Soporte para on/off y caudal
-- =====================================================

-- =====================================================
-- 1. ACTUALIZAR TABLA DE MAPEO ga_integration.ite_aqapi_tag
-- =====================================================

-- Agregar columnas nuevas
ALTER TABLE ga_integration.ite_aqapi_tag 
ADD COLUMN IF NOT EXISTS id BIGSERIAL;

ALTER TABLE ga_integration.ite_aqapi_tag 
ADD COLUMN IF NOT EXISTS tag VARCHAR;

ALTER TABLE ga_integration.ite_aqapi_tag 
ADD COLUMN IF NOT EXISTS tag_cabal VARCHAR;

-- Modificar api_id para que no sea PRIMARY KEY si ya lo es
ALTER TABLE ga_integration.ite_aqapi_tag DROP CONSTRAINT IF EXISTS ite_aqapi_tag_pkey;

-- Copiar idtag existente a tag
UPDATE ga_integration.ite_aqapi_tag 
SET tag = idtag 
WHERE tag IS NULL;

-- Eliminar constraint UNIQUE de idtag si existe
ALTER TABLE ga_integration.ite_aqapi_tag DROP CONSTRAINT IF EXISTS ite_aqapi_tag_idtag_key;

-- Eliminar columna idtag antigua
ALTER TABLE ga_integration.ite_aqapi_tag DROP COLUMN IF EXISTS idtag;

-- Agregar nueva PRIMARY KEY
ALTER TABLE ga_integration.ite_aqapi_tag 
ADD CONSTRAINT ite_aqapi_tag_pk PRIMARY KEY (id);


-- =====================================================
-- 2. ACTUALIZAR TABLA DE HISTÓRICOS ga_landing.ite_aqapi_hist
-- =====================================================

-- Eliminar PRIMARY KEY antigua
ALTER TABLE ga_landing.ite_aqapi_hist DROP CONSTRAINT IF EXISTS ite_aqapi_hist_pkey;

-- Agregar columnas nuevas
ALTER TABLE ga_landing.ite_aqapi_hist 
ADD COLUMN IF NOT EXISTS id VARCHAR(255);

ALTER TABLE ga_landing.ite_aqapi_hist 
ADD COLUMN IF NOT EXISTS valor_on_off INTEGER;

ALTER TABLE ga_landing.ite_aqapi_hist 
ADD COLUMN IF NOT EXISTS valor_caudal FLOAT8;

-- Copiar datos existentes
UPDATE ga_landing.ite_aqapi_hist 
SET valor_on_off = valor 
WHERE valor_on_off IS NULL;

UPDATE ga_landing.ite_aqapi_hist 
SET id = idtag 
WHERE id IS NULL;

-- Eliminar columnas antiguas
ALTER TABLE ga_landing.ite_aqapi_hist DROP COLUMN IF EXISTS idtag;
ALTER TABLE ga_landing.ite_aqapi_hist DROP COLUMN IF EXISTS valor;

-- Agregar nueva PRIMARY KEY
ALTER TABLE ga_landing.ite_aqapi_hist 
ADD CONSTRAINT ite_aqapi_hist_pkey PRIMARY KEY (fecha, id);

-- Actualizar índices
DROP INDEX IF EXISTS ga_landing.idx_ite_aqapi_hist_idtag;
CREATE INDEX IF NOT EXISTS idx_ite_aqapi_hist_idtag ON ga_landing.ite_aqapi_hist(id);


-- =====================================================
-- 3. ACTUALIZAR VISTA
-- =====================================================

CREATE OR REPLACE VIEW ga_landing.v_aqapi_hist_con_ids AS
SELECT 
    f.fecha,
    f.id,
    f.valor_on_off,
    f.valor_caudal,
    m.api_id,
    m.tag,
    m.tag_cabal,
    m.tipus
FROM 
    ga_landing.ite_aqapi_hist f
    LEFT JOIN ga_integration.ite_aqapi_tag m ON f.id::bigint = m.id
ORDER BY 
    f.fecha DESC;

COMMENT ON VIEW ga_landing.v_aqapi_hist_con_ids IS 'Vista con datos históricos incluyendo API IDs y tags';


-- =====================================================
-- 4. COMENTARIOS
-- =====================================================

COMMENT ON COLUMN ga_integration.ite_aqapi_tag.id IS 'ID secuencial del registro';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.tag IS 'ID del tag para on/off';
COMMENT ON COLUMN ga_integration.ite_aqapi_tag.tag_cabal IS 'ID del tag para caudal (válvulas)';

COMMENT ON TABLE ga_landing.ite_aqapi_hist IS 'Datos de programación desde AquaAdvanced (on/off y caudal)';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.id IS 'ID del registro (referencia a ite_aqapi_tag.id)';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.valor_on_off IS 'Valor on/off (0/1)';
COMMENT ON COLUMN ga_landing.ite_aqapi_hist.valor_caudal IS 'Valor de caudal programado (válvulas)';

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
