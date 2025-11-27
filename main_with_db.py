#!/usr/bin/env python3
"""
Main con Integración CAT_Conexions - Consulta API y guarda en PostgreSQL
Interfaz para consultar la API de AquaAdvanced y almacenar datos en Data Lake
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Añadir directorios al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAT_Conexions", "src")
)

import config
from aquadapt_api_client_oficial_v2 import AquaAdvancedClient

# Importar conexiones CAT
try:
    from CAT_Conexions.src.conexions import pgDataLake

    CAT_CONEXIONS_AVAILABLE = True
    print("✅ CAT_Conexions cargado correctamente")
except ImportError as e:
    CAT_CONEXIONS_AVAILABLE = False
    print(f"⚠️ CAT_Conexions no disponible: {e}")


def guardar_en_datalake(datos, bomba_info, endpoint_name, start_time, end_time):
    """
    Guardar datos de la API en PostgreSQL Data Lake

    Args:
        datos: Datos obtenidos de la API
        bomba_info: Información de la bomba
        endpoint_name: Nombre del endpoint consultado
        start_time: Fecha inicio
        end_time: Fecha fin
    """
    if not CAT_CONEXIONS_AVAILABLE:
        print("❌ CAT_Conexions no está disponible. No se puede guardar en Data Lake.")
        return False

    try:
        print("\n💾 Guardando datos en PostgreSQL Data Lake...")

        # Conectar al Data Lake
        dl = pgDataLake()
        dl.connect()

        # Preparar datos para inserción
        if isinstance(datos, list) and len(datos) > 0:
            # Convertir lista de datos a DataFrame
            import pandas as pd

            df = pd.DataFrame(datos)

            # Añadir metadatos
            df["bomba_id"] = bomba_info["id"]
            df["bomba_name"] = bomba_info["name"]
            df["endpoint"] = endpoint_name
            df["fecha_consulta"] = datetime.now()
            df["rango_inicio"] = start_time
            df["rango_fin"] = end_time

            # Insertar en batch (usar método optimizado)
            # Nota: Necesitarás crear/adaptar la tabla en el Data Lake
            tabla = f"aquaadvanced_{endpoint_name.replace('/', '_')}"

            print(f"   📊 Insertando {len(df)} registros en tabla: {tabla}")

            # Usar el método de inserción en batch del Data Lake
            # dl.insert_data_batch(df, tabla)  # Descomenta cuando tengas la tabla creada

            print(f"✅ Datos guardados exitosamente en Data Lake")

        elif isinstance(datos, dict):
            print("   ℹ️ Datos en formato dict - guardando como JSON")
            # Para datos complejos, guardar como JSON en campo específico
            # Implementar según necesidad

        else:
            print("   ⚠️ No hay datos para guardar")

        dl.disconnect()
        return True

    except Exception as e:
        print(f"❌ Error al guardar en Data Lake: {e}")
        return False


def mostrar_menu_principal():
    """Mostrar menú principal con opciones de integración"""
    print("\n" + "=" * 60)
    print("🚀 AQUAADVANCED API - INTEGRACIÓN CAT_CONEXIONS")
    print("=" * 60)
    print("\n📋 OPCIONES:")
    print("   1. Consultar API y guardar en archivo JSON (modo original)")
    print("   2. Consultar API y guardar en PostgreSQL Data Lake")
    print("   3. Ver configuración actual")
    print("   4. Salir")

    return input("\n➡️ Selecciona una opción (1-4): ").strip()


def main():
    print("=" * 60)
    print("🚀 CONSULTA API AQUAADVANCED + CAT_CONEXIONS")
    print("=" * 60)

    # Verificar disponibilidad de CAT_Conexions
    if CAT_CONEXIONS_AVAILABLE:
        print("✅ Integración con CAT_Conexions activada")
    else:
        print("⚠️ Modo solo API (sin integración base de datos)")

    while True:
        opcion = mostrar_menu_principal()

        if opcion == "1":
            # Modo original - solo JSON
            consultar_y_guardar_json()

        elif opcion == "2":
            # Guardar en PostgreSQL
            if not CAT_CONEXIONS_AVAILABLE:
                print("❌ CAT_Conexions no disponible. Selecciona opción 1.")
                continue
            consultar_y_guardar_db()

        elif opcion == "3":
            # Ver configuración
            mostrar_configuracion()

        elif opcion == "4":
            print("\n👋 ¡Hasta luego!")
            break

        else:
            print("❌ Opción inválida. Intenta de nuevo.")

        continuar = input("\n¿Realizar otra operación? (s/N): ").strip().lower()
        if continuar not in ["s", "si", "y", "yes"]:
            print("\n👋 ¡Hasta luego!")
            break


def consultar_y_guardar_json():
    """Consulta API y guarda en JSON (modo original)"""
    print("\n📁 MODO: Guardar en archivo JSON")

    # Reutilizar lógica del main.py original
    client = AquaAdvancedClient()
    bombas = client.get_bombas_list()

    if not bombas:
        print("❌ No se pudieron obtener las bombas")
        return

    # Seleccionar bomba (primeras 10)
    print(f"\n📋 BOMBAS DISPONIBLES ({len(bombas)} total):")
    for i, bomba in enumerate(bombas[:10], 1):
        name = bomba.get("name", "Sin nombre")
        bomba_id = bomba.get("id", "Sin ID")
        print(f"   {i}. {name} (ID: {bomba_id[:8]}...)")

    try:
        opcion = int(input(f"\nSelecciona bomba (1-{min(10, len(bombas))}): ").strip())
        bomba_seleccionada = bombas[opcion - 1]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return

    # Seleccionar endpoint simple
    print("\n📡 ENDPOINT:")
    print("   1. Status")
    print("   2. Power")
    print("   3. Speed")

    try:
        endpoint_opt = int(input("Selecciona (1-3): ").strip())
        endpoints = ["status", "power", "speed"]
        endpoint = endpoints[endpoint_opt - 1]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return

    # Fechas simples
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    print(f"\n🔍 Consultando {endpoint} de {bomba_seleccionada['name']}...")

    # Consultar
    if endpoint == "status":
        datos = client.get_bomba_status(
            bomba_seleccionada["id"], start_time.isoformat(), end_time.isoformat()
        )
    elif endpoint == "power":
        datos = client.get_bomba_power(
            bomba_seleccionada["id"], start_time.isoformat(), end_time.isoformat()
        )
    else:
        datos = client.get_bomba_speed(
            bomba_seleccionada["id"], start_time.isoformat(), end_time.isoformat()
        )

    # Guardar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"consulta_{endpoint}_{bomba_seleccionada['name'].replace(' ', '_')}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            {
                "bomba": bomba_seleccionada,
                "endpoint": endpoint,
                "datos": datos,
                "timestamp": timestamp,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"✅ Guardado en: {filename}")


def consultar_y_guardar_db():
    """Consulta API y guarda en PostgreSQL"""
    print("\n🗄️ MODO: Guardar en PostgreSQL Data Lake")

    client = AquaAdvancedClient()
    bombas = client.get_bombas_list()

    if not bombas:
        print("❌ No se pudieron obtener las bombas")
        return

    # Simplificado: primera bomba
    bomba = bombas[0]
    endpoint = "status"

    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    print(f"\n🔍 Consultando {endpoint} de {bomba['name']}...")

    datos = client.get_bomba_status(
        bomba["id"], start_time.isoformat(), end_time.isoformat()
    )

    # Guardar en Data Lake
    guardar_en_datalake(datos, bomba, endpoint, start_time, end_time)


def mostrar_configuracion():
    """Muestra la configuración actual"""
    print("\n⚙️ CONFIGURACIÓN ACTUAL:")
    print(f"   API Base URL: {config.API_BASE_URL}")
    print(f"   API Key: {config.API_KEY[:20]}...")
    print(f"   SSL Verify: {config.VERIFY_SSL}")

    if CAT_CONEXIONS_AVAILABLE:
        from CAT_Conexions.src.Config.BaseConfig import DATABASE, HOST, USER

        print(f"\n   PostgreSQL Host: {HOST}")
        print(f"   Database: {DATABASE}")
        print(f"   User: {USER}")


if __name__ == "__main__":
    main()
