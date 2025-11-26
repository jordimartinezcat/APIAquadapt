-- =====================================================
-- Script para modificar tabla ite_aqapi_hist
-- Eliminar id y fecha_insercion, establecer PK compuesta
-- =====================================================

-- 1. Eliminar constraint UNIQUE (ya no es necesario con PK compuesta)
ALTER TABLE ga_landing.ite_aqapi_hist DROP CONSTRAINT IF EXISTS uk_fecha_idtag;

-- 2. Eliminar PRIMARY KEY actual
ALTER TABLE ga_landing.ite_aqapi_hist DROP CONSTRAINT IF EXISTS ite_aqapi_hist_pkey;

-- 3. Eliminar columna id
ALTER TABLE ga_landing.ite_aqapi_hist DROP COLUMN IF EXISTS id;

-- 4. Eliminar columna fecha_insercion
ALTER TABLE ga_landing.ite_aqapi_hist DROP COLUMN IF EXISTS fecha_insercion;

-- 5. Establecer PRIMARY KEY compuesta (fecha, idtag)
ALTER TABLE ga_landing.ite_aqapi_hist ADD PRIMARY KEY (fecha, idtag);

-- 6. Eliminar índice redundante (ya incluido en PK)
DROP INDEX IF EXISTS ga_landing.idx_ite_aqapi_hist_fecha_idtag;

-- 7. Actualizar comentario de la tabla
COMMENT ON TABLE ga_landing.ite_aqapi_hist IS 'Datos de programación on/off desde AquaAdvanced - PK: (fecha, idtag)';
