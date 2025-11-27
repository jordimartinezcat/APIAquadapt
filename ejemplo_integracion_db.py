#!/usr/bin/env python3
"""
Ejemplo de Integración: AquaAdvanced API + CAT_Conexions
Demuestra cómo consultar la API y almacenar datos en PostgreSQL
"""

import os
import sys
from datetime import datetime, timedelta

import pandas as pd

# Añadir paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAT_Conexions", "src")
)

# Importar cliente API AquaAdvanced
from aquadapt_api_client_oficial_v2 import AquaAdvancedClient

# Importar conexiones CAT
try:
    from CAT_Conexions.src.conexions import pgDataLake

    CAT_DISPONIBLE = True
except ImportError as e:
    print(f"⚠️ CAT_Conexions no disponible: {e}")
    CAT_DISPONIBLE = False


def ejemplo_1_consulta_simple():
    """
    Ejemplo 1: Consulta básica de la API
    """
    print("\n" + "=" * 70)
    print("📊 EJEMPLO 1: Consulta Simple de API")
    print("=" * 70)

    # Inicializar cliente
    client = AquaAdvancedClient()

    # Obtener lista de bombas
    print("\n1️⃣ Obteniendo lista de bombas...")
    bombas = client.get_bombas_list()
    print(f"   ✅ {len(bombas)} bombas encontradas")

    # Seleccionar primera bomba
    bomba = bombas[0]
    print(f"\n2️⃣ Bomba seleccionada: {bomba['name']}")
    print(f"   ID: {bomba['id']}")

    # Consultar status de últimas 24 horas
    print("\n3️⃣ Consultando status (últimas 24h)...")
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    datos = client.get_bomba_status(
        bomba["id"], start_time.isoformat(), end_time.isoformat(), detailed=False
    )

    print(f"   ✅ Datos obtenidos: {len(datos) if isinstance(datos, list) else 'dict'}")

    if isinstance(datos, list) and len(datos) > 0:
        print(f"\n4️⃣ Muestra de datos (primeros 3):")
        for i, registro in enumerate(datos[:3], 1):
            print(f"   {i}. {registro}")
    else:
        print(f"\n4️⃣ No hay datos para el rango especificado")

    return bomba, datos, start_time, end_time


def ejemplo_2_guardar_postgresql(bomba, datos, start_time, end_time):
    """
    Ejemplo 2: Guardar datos en PostgreSQL Data Lake
    """
    print("\n" + "=" * 70)
    print("💾 EJEMPLO 2: Guardar en PostgreSQL Data Lake")
    print("=" * 70)

    if not CAT_DISPONIBLE:
        print("\n❌ CAT_Conexions no está disponible. Saltando ejemplo.")
        return

    if not isinstance(datos, list) or len(datos) == 0:
        print("\n⚠️ No hay datos para guardar")
        return

    try:
        # Convertir datos a DataFrame
        print("\n1️⃣ Convirtiendo datos a DataFrame...")
        df = pd.DataFrame(datos)

        # Añadir metadatos
        df["bomba_id"] = bomba["id"]
        df["bomba_name"] = bomba["name"]
        df["fecha_consulta"] = datetime.now()
        df["rango_inicio"] = start_time
        df["rango_fin"] = end_time

        print(f"   ✅ DataFrame creado: {len(df)} filas x {len(df.columns)} columnas")
        print(f"\n   Columnas: {list(df.columns)}")

        # Conectar a Data Lake
        print("\n2️⃣ Conectando a PostgreSQL Data Lake...")
        dl = pgDataLake()
        dl.connect()
        print("   ✅ Conexión establecida")

        # Mostrar primeras filas
        print("\n3️⃣ Vista previa de datos a insertar:")
        print(df.head(3).to_string())

        # NOTA: Para insertar realmente, necesitas:
        # - Crear la tabla en PostgreSQL
        # - Adaptar el método de inserción según tu esquema

        print("\n4️⃣ Insertando datos...")
        print("   ⚠️ SIMULADO - Necesitas crear tabla en PostgreSQL primero")
        print(f"   Tabla sugerida: aquaadvanced_status")
        print(f"   Esquema sugerido: ga_datalake")

        # Ejemplo de query que crearías:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ga_datalake.aquaadvanced_status (
            id SERIAL PRIMARY KEY,
            bomba_id VARCHAR(255),
            bomba_name VARCHAR(255),
            timestamp TIMESTAMP,
            value FLOAT,
            fecha_consulta TIMESTAMP,
            rango_inicio TIMESTAMP,
            rango_fin TIMESTAMP
        );
        """
        print(f"\n   📝 Query sugerida para crear tabla:")
        print(f"   {create_table_query}")

        # Para insertar realmente (descomenta cuando tengas la tabla):
        # dl.insert_data_batch(df, 'aquaadvanced_status')

        dl.disconnect()
        print("\n   ✅ Desconectado de Data Lake")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def ejemplo_3_consulta_multiple_endpoints():
    """
    Ejemplo 3: Consultar múltiples endpoints y consolidar
    """
    print("\n" + "=" * 70)
    print("🔄 EJEMPLO 3: Consulta Múltiple de Endpoints")
    print("=" * 70)

    client = AquaAdvancedClient()
    bombas = client.get_bombas_list()

    if not bombas:
        print("❌ No se pudieron obtener bombas")
        return

    # Seleccionar bomba
    bomba = bombas[0]
    print(f"\n📍 Bomba: {bomba['name']}")

    # Fechas
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=6)

    print(
        f"\n⏰ Rango: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
    )

    # Consultar múltiples endpoints
    endpoints = {
        "status": lambda: client.get_bomba_status(
            bomba["id"], start_time.isoformat(), end_time.isoformat()
        ),
        "power": lambda: client.get_bomba_power(
            bomba["id"], start_time.isoformat(), end_time.isoformat()
        ),
        "speed": lambda: client.get_bomba_speed(
            bomba["id"], start_time.isoformat(), end_time.isoformat()
        ),
    }

    resultados = {}

    for nombre, consulta_fn in endpoints.items():
        print(f"\n   🔍 Consultando {nombre}...")
        try:
            datos = consulta_fn()
            puntos = len(datos) if isinstance(datos, list) else 0
            resultados[nombre] = datos
            print(f"      ✅ {puntos} puntos de datos")
        except Exception as e:
            print(f"      ❌ Error: {e}")
            resultados[nombre] = []

    # Resumen
    print("\n📊 RESUMEN DE CONSULTAS:")
    total_puntos = sum(
        len(v) if isinstance(v, list) else 0 for v in resultados.values()
    )
    print(f"   Total de puntos obtenidos: {total_puntos}")

    for nombre, datos in resultados.items():
        puntos = len(datos) if isinstance(datos, list) else 0
        status = "✅" if puntos > 0 else "⚠️"
        print(f"   {status} {nombre}: {puntos} puntos")

    return resultados


def ejemplo_4_analisis_tendencias():
    """
    Ejemplo 4: Análisis básico de tendencias
    """
    print("\n" + "=" * 70)
    print("📈 EJEMPLO 4: Análisis de Tendencias")
    print("=" * 70)

    client = AquaAdvancedClient()
    bombas = client.get_bombas_list()

    if not bombas:
        return

    bomba = bombas[0]
    print(f"\n📍 Analizando: {bomba['name']}")

    # Consultar última semana
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    print(f"⏰ Periodo: Última semana")
    print(f"   Desde: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Hasta: {end_time.strftime('%Y-%m-%d %H:%M')}")

    print("\n🔍 Consultando datos de potencia...")
    datos_power = client.get_bomba_power(
        bomba["id"], start_time.isoformat(), end_time.isoformat()
    )

    if isinstance(datos_power, list) and len(datos_power) > 0:
        # Convertir a DataFrame para análisis
        df = pd.DataFrame(datos_power)

        print(f"\n✅ Datos obtenidos: {len(df)} registros")
        print(f"\n📊 ESTADÍSTICAS:")

        if "value" in df.columns:
            print(f"   Media: {df['value'].mean():.2f}")
            print(f"   Mínimo: {df['value'].min():.2f}")
            print(f"   Máximo: {df['value'].max():.2f}")
            print(f"   Desv. Est.: {df['value'].std():.2f}")
        else:
            print("   ⚠️ Columna 'value' no encontrada en datos")
            print(f"   Columnas disponibles: {list(df.columns)}")

    else:
        print("\n⚠️ No hay datos disponibles para el análisis")


def main():
    """
    Ejecutar todos los ejemplos
    """
    print("\n" + "=" * 70)
    print("🚀 EJEMPLOS DE INTEGRACIÓN: AquaAdvanced + CAT_Conexions")
    print("=" * 70)

    print("\n📝 Este script demuestra:")
    print("   1. Consulta básica de la API")
    print("   2. Almacenamiento en PostgreSQL (simulado)")
    print("   3. Consulta múltiple de endpoints")
    print("   4. Análisis básico de tendencias")

    input("\n▶️ Presiona Enter para comenzar...")

    # Ejemplo 1: Consulta simple
    bomba, datos, start_time, end_time = ejemplo_1_consulta_simple()

    input("\n▶️ Presiona Enter para continuar al Ejemplo 2...")

    # Ejemplo 2: Guardar en PostgreSQL
    ejemplo_2_guardar_postgresql(bomba, datos, start_time, end_time)

    input("\n▶️ Presiona Enter para continuar al Ejemplo 3...")

    # Ejemplo 3: Múltiples endpoints
    ejemplo_3_consulta_multiple_endpoints()

    input("\n▶️ Presiona Enter para continuar al Ejemplo 4...")

    # Ejemplo 4: Análisis de tendencias
    ejemplo_4_analisis_tendencias()

    print("\n" + "=" * 70)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("=" * 70)
    print("\n💡 Próximos pasos:")
    print("   - Crear tablas en PostgreSQL para almacenamiento permanente")
    print("   - Configurar jobs automáticos de consulta")
    print("   - Implementar dashboards de visualización")
    print("   - Integrar alertas basadas en umbrales")


if __name__ == "__main__":
    main()
    main()
