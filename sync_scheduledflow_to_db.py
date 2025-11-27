#!/usr/bin/env python3
"""
Sync OnOffSchedule to Database - Script para Apache NiFi
Script automatizado para consultar onoffschedule de bombas/válvulas
y almacenar en PostgreSQL usando mapeo de tags.

Ejecutar periódicamente desde Apache NiFi para sincronización continua.
"""

import logging
import os
import sys
from datetime import datetime, timedelta

import pandas as pd

# Añadir paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAT_Conexions", "src")
)

import config
from aquadapt_api_client_oficial_v2 import AquaAdvancedClient

# Importar conexión PostgreSQL
try:
    from CAT_Conexions.src.conexions import pgDataLake

    DB_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: CAT_Conexions no disponible: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sync_scheduledflow.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Configuración
SCHEMA_INTEGRATION = "ga_integration"
SCHEMA_LANDING = "ga_landing"
TABLE_MAPPING = "ite_aqapi_tag"
TABLE_TARGET = "ite_aqapi_hist"


def calcular_fechas():
    """
    Calcular fechas de inicio y fin según las reglas de negocio:
    
    - start_time: Hora actual redondeada hacia abajo a la media hora más cercana (:00 o :30)
    - end_time: 
        * Si hora actual < 08:00 → (día actual + 1) a las 08:00
        * Si hora actual >= 08:00 → (día actual + 2) a las 08:00
    
    Returns:
        tuple: (start_time, end_time) ambos como datetime
    """
    now = datetime.now()
    
    # FECHA INICIO: Redondear hacia abajo a :00 o :30
    if now.minute < 30:
        # Redondear a :00
        start_time = now.replace(minute=0, second=0, microsecond=0)
    else:
        # Redondear a :30
        start_time = now.replace(minute=30, second=0, microsecond=0)
    
    # FECHA FINAL: Lógica basada en la hora de corte de las 08:00
    if now.hour < 8:
        # Antes de las 08:00 → mañana a las 08:00
        end_time = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        # A partir de las 08:00 → pasado mañana a las 08:00
        end_time = (now + timedelta(days=2)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    return start_time, end_time


class OnOffScheduleSync:
    """Clase para sincronizar datos de onoffschedule a PostgreSQL"""

    def __init__(self):
        self.client = AquaAdvancedClient()
        self.db = pgDataLake()
        self.mapping_cache = None

    def conectar_db(self):
        """Conectar a PostgreSQL"""
        try:
            self.db.connect()
            logger.info("✅ Conectado a PostgreSQL Data Lake")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False

    def desconectar_db(self):
        """Desconectar de PostgreSQL"""
        try:
            self.db.disconnect()
            logger.info("✅ Desconectado de PostgreSQL")
        except Exception as e:
            logger.error(f"⚠️ Error desconectando: {e}")

    def obtener_mapeo_tags(self):
        """
        Obtener mapeo de IDs API a IDs desde tabla de integración

        Returns:
            DataFrame con columnas: id, api_id, tag, tag_cabal, tipus
        """
        try:
            query = f"""
            SELECT 
                id,
                api_id,
                tag,
                tag_cabal,
                tipus
            FROM {SCHEMA_INTEGRATION}.{TABLE_MAPPING}
            ORDER BY api_id;
            """

            logger.info(
                f"📊 Obteniendo mapeo de tags desde {SCHEMA_INTEGRATION}.{TABLE_MAPPING}"
            )
            self.db.connect_database()
            df_mapping = self.db.get_data(query)

            if df_mapping is not None and len(df_mapping) > 0:
                logger.info(f"✅ Mapeo obtenido: {len(df_mapping)} registros")
                self.mapping_cache = df_mapping
                return df_mapping
            else:
                logger.warning("⚠️ No se encontró mapeo de tags")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"❌ Error obteniendo mapeo: {e}")
            return pd.DataFrame()

    def obtener_bombas(self):
        """Obtener lista de bombas desde la API"""
        try:
            logger.info("🔍 Obteniendo lista de bombas...")
            bombas = self.client.get_bombas_list()
            logger.info(f"✅ Bombas obtenidas: {len(bombas)}")
            return bombas
        except Exception as e:
            logger.error(f"❌ Error obteniendo bombas: {e}")
            return []

    def obtener_valvulas(self):
        """Obtener lista de válvulas desde la API"""
        try:
            logger.info("🔍 Obteniendo lista de válvulas...")
            # Usar el endpoint de válvulas
            valvulas = self.client.get_valves_list()
            logger.info(f"✅ Válvulas obtenidas: {len(valvulas)}")
            return valvulas
        except Exception as e:
            logger.error(f"❌ Error obteniendo válvulas: {e}")
            return []

    def consultar_onoffschedule(self, device_id, device_name, device_tipo, start_time, end_time):
        """
        Consultar onoffschedule para un dispositivo

        Args:
            device_id: ID del dispositivo (bomba o válvula)
            device_name: Nombre del dispositivo
            device_tipo: Tipo de dispositivo ('bomba' o 'valvula')
            start_time: Fecha/hora inicio
            end_time: Fecha/hora fin

        Returns:
            Lista de registros con datos
        """
        try:
            logger.info(f"   📡 Consultando onoffschedule de: {device_name} ({device_tipo})")

            # Usar endpoint correcto según el tipo
            if device_tipo == 'bomba':
                datos = self.client.get_bomba_onoffschedule(
                    device_id, start_time.isoformat(), end_time.isoformat()
                )
            elif device_tipo == 'valvula':
                # Para válvulas, usar endpoint específico de válvulas
                datos = self.client.get_valve_onoffschedule(
                    device_id, start_time.isoformat(), end_time.isoformat()
                )
            else:
                logger.warning(f"      ⚠️ Tipo desconocido: {device_tipo}")
                return []

            if isinstance(datos, list):
                logger.info(f"      ✅ {len(datos)} registros obtenidos")
                return datos
            else:
                logger.warning(f"      ⚠️ Respuesta inesperada: {type(datos)}")
                return []

        except Exception as e:
            logger.error(f"      ❌ Error consultando onoffschedule: {e}")
            return []

    def consultar_scheduledflow(self, device_id, device_name, start_time, end_time):
        """
        Consultar scheduledflow para una válvula (caudal programado)

        Args:
            device_id: ID de la válvula
            device_name: Nombre de la válvula
            start_time: Fecha/hora inicio
            end_time: Fecha/hora fin

        Returns:
            Lista de registros con datos de caudal
        """
        try:
            logger.info(f"   📡 Consultando scheduledflow (caudal) de: {device_name}")

            datos = self.client.get_valve_scheduledflow(
                device_id, start_time.isoformat(), end_time.isoformat()
            )

            if isinstance(datos, list):
                logger.info(f"      ✅ {len(datos)} registros de caudal obtenidos")
                return datos
            else:
                logger.warning(f"      ⚠️ Respuesta inesperada: {type(datos)}")
                return []

        except Exception as e:
            logger.error(f"      ❌ Error consultando scheduledflow: {e}")
            return []

    def transformar_datos(self, datos_raw, api_id, record_id, device_name):
        """
        Transformar datos de API al formato de tabla destino

        Args:
            datos_raw: Datos crudos de la API
            api_id: ID de la API
            record_id: ID del registro para insertar
            device_name: Nombre del dispositivo

        Returns:
            DataFrame con columnas: fecha, id, valor_on_off
        """
        if not datos_raw or len(datos_raw) == 0:
            return pd.DataFrame(columns=["fecha", "id", "valor_on_off"])

        try:
            # Convertir a DataFrame
            df = pd.DataFrame(datos_raw)

            # Transformar según estructura esperada
            df_transformed = pd.DataFrame()

            # Mapear columnas (ajustar según respuesta real de API)
            if "timestamp" in df.columns:
                df_transformed["fecha"] = pd.to_datetime(df["timestamp"])
            elif "time" in df.columns:
                df_transformed["fecha"] = pd.to_datetime(df["time"])
            else:
                logger.warning(
                    f"⚠️ No se encontró columna de fecha en datos de {device_name}"
                )
                df_transformed["fecha"] = datetime.now()

            # Asignar id
            df_transformed["id"] = record_id

            # Extraer valor on/off (ajustar según estructura de respuesta)
            if "value" in df.columns:
                df_transformed["valor_on_off"] = df["value"]
            elif "flowrate" in df.columns:
                df_transformed["valor_on_off"] = df["flowrate"]
            elif "setpoint" in df.columns:
                df_transformed["valor_on_off"] = df["setpoint"]
            else:
                logger.warning(
                    f"⚠️ No se encontró columna de valor en datos de {device_name}"
                )
                df_transformed["valor_on_off"] = None

            # Filtrar nulls
            df_transformed = df_transformed.dropna(subset=["valor_on_off"])

            logger.info(
                f"      🔄 Transformados {len(df_transformed)} registros para id={record_id}"
            )

            return df_transformed

        except Exception as e:
            logger.error(f"❌ Error transformando datos de {device_name}: {e}")
            return pd.DataFrame(columns=["fecha", "id", "valor_on_off"])

    def transformar_datos_caudal(self, datos_raw, record_id, device_name):
        """
        Transformar datos de caudal (scheduledflow) de API al formato de tabla destino

        Args:
            datos_raw: Datos crudos de la API (scheduledflow)
            record_id: ID del registro para insertar
            device_name: Nombre del dispositivo

        Returns:
            DataFrame con columnas: fecha, id, valor_caudal
        """
        if not datos_raw or len(datos_raw) == 0:
            return pd.DataFrame(columns=["fecha", "id", "valor_caudal"])

        try:
            # Convertir a DataFrame
            df = pd.DataFrame(datos_raw)

            # Transformar según estructura esperada
            df_transformed = pd.DataFrame()

            # Mapear columnas (ajustar según respuesta real de API)
            if "timestamp" in df.columns:
                df_transformed["fecha"] = pd.to_datetime(df["timestamp"])
            elif "time" in df.columns:
                df_transformed["fecha"] = pd.to_datetime(df["time"])
            else:
                logger.warning(
                    f"⚠️ No se encontró columna de fecha en datos de caudal de {device_name}"
                )
                df_transformed["fecha"] = datetime.now()

            # Asignar id
            df_transformed["id"] = record_id

            # Extraer valor de caudal
            if "value" in df.columns:
                df_transformed["valor_caudal"] = df["value"]
            elif "flowrate" in df.columns:
                df_transformed["valor_caudal"] = df["flowrate"]
            elif "setpoint" in df.columns:
                df_transformed["valor_caudal"] = df["setpoint"]
            else:
                logger.warning(
                    f"⚠️ No se encontró columna de caudal en datos de {device_name}"
                )
                df_transformed["valor_caudal"] = None

            # Filtrar nulls
            df_transformed = df_transformed.dropna(subset=["valor_caudal"])

            logger.info(
                f"      🔄 Transformados {len(df_transformed)} registros de caudal para id={record_id}"
            )

            return df_transformed

        except Exception as e:
            logger.error(f"❌ Error transformando datos de caudal de {device_name}: {e}")
            return pd.DataFrame(columns=["fecha", "id", "valor_caudal"])

    def insertar_datos(self, df_datos):
        """
        Insertar datos en tabla destino usando inserción batch optimizada

        Args:
            df_datos: DataFrame con columnas fecha, id, valor_on_off, valor_caudal (opcional)
        """
        if df_datos is None or len(df_datos) == 0:
            logger.info("ℹ️ No hay datos para insertar")
            return 0

        try:
            logger.info(
                f"💾 Insertando {len(df_datos)} registros en {SCHEMA_LANDING}.{TABLE_TARGET}..."
            )

            self.db.connect_database()

            # Convertir fecha a string ISO para inserción
            df_insert = df_datos.copy()
            df_insert["fecha"] = df_insert["fecha"].dt.strftime("%Y-%m-%d %H:%M:%S")

            # Asegurar tipos de datos correctos
            if "valor_on_off" in df_insert.columns:
                df_insert["valor_on_off"] = df_insert["valor_on_off"].fillna(0).astype(int)
            
            if "valor_caudal" in df_insert.columns:
                df_insert["valor_caudal"] = df_insert["valor_caudal"].astype(float)

            # Inserción batch optimizada: construir un solo INSERT con múltiples VALUES
            BATCH_SIZE = 500  # Insertar de 500 en 500
            total_inserted = 0
            
            for i in range(0, len(df_insert), BATCH_SIZE):
                batch = df_insert.iloc[i:i+BATCH_SIZE]
                
                # Construir VALUES para este batch
                values_list = []
                for _, row in batch.iterrows():
                    valor_on_off = row.get('valor_on_off', 'NULL')
                    valor_caudal = row.get('valor_caudal', 'NULL')
                    
                    # Formatear NULL correctamente
                    valor_on_off_str = 'NULL' if pd.isna(valor_on_off) else str(int(valor_on_off))
                    valor_caudal_str = 'NULL' if pd.isna(valor_caudal) else str(float(valor_caudal))
                    
                    values_list.append(
                        f"('{row['fecha']}', '{row['id']}', {valor_on_off_str}, {valor_caudal_str})"
                    )
                
                values_str = ",\n                ".join(values_list)
                
                query = f"""
                INSERT INTO {SCHEMA_LANDING}.{TABLE_TARGET} (fecha, id, valor_on_off, valor_caudal)
                VALUES 
                {values_str}
                ON CONFLICT (fecha, id) DO UPDATE 
                SET valor_on_off = COALESCE(EXCLUDED.valor_on_off, {SCHEMA_LANDING}.{TABLE_TARGET}.valor_on_off),
                    valor_caudal = COALESCE(EXCLUDED.valor_caudal, {SCHEMA_LANDING}.{TABLE_TARGET}.valor_caudal);
                """
                
                self.db.get_data(query)
                total_inserted += len(batch)
                
                if (i + BATCH_SIZE) < len(df_insert):
                    logger.info(f"   ⏳ Progreso: {total_inserted}/{len(df_insert)} registros insertados...")

            logger.info(f"✅ {total_inserted} datos insertados correctamente")
            return total_inserted

        except Exception as e:
            logger.error(f"❌ Error insertando datos: {e}")
            return 0

    def procesar_dispositivos(self, bombas, valvulas, mapping_df, start_time, end_time):
        """
        Procesar lista de dispositivos separando bombas y válvulas

        Args:
            bombas: Lista de bombas desde API
            valvulas: Lista de válvulas desde API
            mapping_df: DataFrame con mapeo de IDs (incluye columna 'tipus')
            start_time: Fecha inicio
            end_time: Fecha fin

        Returns:
            DataFrame consolidado con todos los datos
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"📦 PROCESANDO DISPOSITIVOS")
        logger.info(f"{'='*70}")

        if len(mapping_df) == 0:
            logger.warning(f"⚠️ No hay mapeo definido")
            return pd.DataFrame()

        logger.info(f"📋 {len(mapping_df)} dispositivos en mapeo")

        # Separar por tipo
        mapping_bombas = mapping_df[mapping_df['tipus'] == 'bomba']
        mapping_valvulas = mapping_df[mapping_df['tipus'] == 'valvula']
        
        logger.info(f"   - Bombas en mapeo: {len(mapping_bombas)}")
        logger.info(f"   - Válvulas en mapeo: {len(mapping_valvulas)}")

        # DataFrame para acumular todos los datos
        df_todos = pd.DataFrame()

        # Procesar bombas
        logger.info(f"\n🔧 Procesando BOMBAS...")
        for _, map_row in mapping_bombas.iterrows():
            api_id = map_row["api_id"]
            record_id = map_row["id"]

            # Buscar bomba en lista de API
            bomba = next((b for b in bombas if b.get("id") == api_id), None)

            if bomba is None:
                logger.warning(f"⚠️ Bomba {api_id[:8]}... no encontrada en API")
                continue

            nombre_bomba = bomba.get("name", api_id[:8])

            # Consultar onoffschedule
            datos_raw = self.consultar_onoffschedule(
                api_id, nombre_bomba, 'bomba', start_time, end_time
            )

            if len(datos_raw) > 0:
                df_device = self.transformar_datos(
                    datos_raw, api_id, record_id, nombre_bomba
                )
                if len(df_device) > 0:
                    df_todos = pd.concat([df_todos, df_device], ignore_index=True)

        # Procesar válvulas
        logger.info(f"\n🚰 Procesando VÁLVULAS...")
        for _, map_row in mapping_valvulas.iterrows():
            api_id = map_row["api_id"]
            record_id = map_row["id"]

            # Buscar válvula en lista de API
            valvula = next((v for v in valvulas if v.get("id") == api_id), None)

            if valvula is None:
                logger.warning(f"⚠️ Válvula {api_id[:8]}... no encontrada en API")
                continue

            nombre_valvula = valvula.get("name", api_id[:8])

            # Consultar onoffschedule
            datos_raw_onoff = self.consultar_onoffschedule(
                api_id, nombre_valvula, 'valvula', start_time, end_time
            )

            if len(datos_raw_onoff) > 0:
                df_onoff = self.transformar_datos(
                    datos_raw_onoff, api_id, record_id, nombre_valvula
                )
                
                # Para válvulas, consultar también scheduledflow (caudal)
                datos_raw_caudal = self.consultar_scheduledflow(
                    api_id, nombre_valvula, start_time, end_time
                )
                
                if len(datos_raw_caudal) > 0:
                    df_caudal = self.transformar_datos_caudal(
                        datos_raw_caudal, record_id, nombre_valvula
                    )
                    
                    # Combinar on/off con caudal usando merge por fecha e id
                    if len(df_caudal) > 0:
                        df_device = pd.merge(
                            df_onoff, 
                            df_caudal, 
                            on=['fecha', 'id'], 
                            how='outer'
                        )
                    else:
                        df_device = df_onoff
                else:
                    df_device = df_onoff
                
                if len(df_device) > 0:
                    df_todos = pd.concat([df_todos, df_device], ignore_index=True)

        logger.info(f"\n📊 RESUMEN TOTAL:")
        logger.info(f"   Total registros: {len(df_todos)}")

        return df_todos

    def ejecutar_sincronizacion(self):
        """
        Ejecutar proceso completo de sincronización
        """
        logger.info("\n" + "=" * 70)
        logger.info("🚀 INICIANDO SINCRONIZACIÓN ONOFFSCHEDULE")
        logger.info("=" * 70)
        logger.info(
            f"📅 Fecha ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Definir ventana temporal con lógica de media hora y corte 08:00
        start_time, end_time = calcular_fechas()

        logger.info("⏰ Ventana temporal (media hora + corte 08:00):")
        logger.info(f"   Desde: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Hasta: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Conectar a base de datos
        if not self.conectar_db():
            logger.error("❌ No se pudo conectar a la base de datos. Abortando.")
            return False

        try:
            # 1. Obtener mapeo de tags
            mapping_df = self.obtener_mapeo_tags()
            if len(mapping_df) == 0:
                logger.error("❌ No se pudo obtener mapeo. Abortando.")
                return False

            # 2. Obtener bombas y válvulas (listas separadas)
            bombas = self.obtener_bombas()
            valvulas = self.obtener_valvulas()

            logger.info(
                f"\n📋 Total dispositivos disponibles: {len(bombas) + len(valvulas)}"
            )
            logger.info(f"   - Bombas: {len(bombas)}")
            logger.info(f"   - Válvulas: {len(valvulas)}")

            # 3. Procesar dispositivos separados por tipo
            df_total = self.procesar_dispositivos(
                bombas, valvulas, mapping_df, start_time, end_time
            )

            # 4. Insertar en base de datos
            if len(df_total) > 0:
                registros_insertados = self.insertar_datos(df_total)
                logger.info(
                    f"\n✅ Sincronización completada: {registros_insertados} registros"
                )
                return True
            else:
                logger.info("\nℹ️ No hay datos para sincronizar")
                return True

        except Exception as e:
            logger.error(f"\n❌ Error en sincronización: {e}")
            return False

        finally:
            self.desconectar_db()


def main():
    """Función principal"""
    try:
        sync = OnOffScheduleSync()
        exito = sync.ejecutar_sincronizacion()

        if exito:
            logger.info("\n" + "=" * 70)
            logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            sys.exit(0)
        else:
            logger.error("\n" + "=" * 70)
            logger.error("❌ PROCESO FINALIZADO CON ERRORES")
            logger.error("=" * 70)
            sys.exit(1)

    except Exception as e:
        logger.critical(f"\n💥 ERROR CRÍTICO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    main()
