#!/usr/bin/env python3
"""
Main - Consulta Simple API AquaAdvanced
Interfaz simple para consultar la API con fechas personalizables
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from aquadapt_api_client_oficial_v2 import AquaAdvancedClient


def mostrar_menu_endpoints():
    """Mostrar endpoints disponibles para bomba"""
    print("\n📡 ENDPOINTS DISPONIBLES PARA BOMBAS:")
    endpoints_bomba = [
        ("1", "status", "Estado actual de la bomba"),
        ("2", "detailed_status", "Estado detallado"),
        ("3", "power", "Potencia (rawpower)"),
        ("4", "detailed_power", "Potencia detallada"),
        ("5", "speed", "Velocidad"),
        ("6", "detailed_speed", "Velocidad detallada"),
        ("7", "faults", "Fallos/Errores"),
        ("8", "detailed_faults", "Fallos detallados"),
        ("9", "control", "Control AAE"),
        ("10", "detailed_control", "Control AAE detallado"),
        ("11", "inservice", "En servicio"),
        ("12", "detailed_inservice", "En servicio detallado"),
        ("13", "onoffschedule", "Programaciones marcha/paro"),
        ("14", "detailed_onoffschedule", "Programaciones marcha/paro detalladas"),
        ("15", "all_basic", "🔥 TODOS los básicos (status, power, speed)"),
        ("16", "all_detailed", "🔥 TODOS los detallados"),
    ]

    for num, endpoint, desc in endpoints_bomba:
        print(f"   {num}. {endpoint} - {desc}")

    return endpoints_bomba


def obtener_fechas():
    """Obtener fechas de inicio y fin del usuario"""
    print("\n📅 CONFIGURACIÓN DE FECHAS:")
    print("Formatos aceptados:")
    print("  - 'hoy' o 'today' = últimas 24 horas")
    print("  - 'ayer' o 'yesterday' = ayer")
    print("  - 'semana' o 'week' = última semana")
    print("  - Fecha específica: 2025-10-23 o 2025-10-23 14:30")

    # Fecha inicio
    while True:
        start_input = input(
            "\n🕐 Fecha/hora inicio (o presiona Enter para 'hoy'): "
        ).strip()

        if not start_input or start_input.lower() in ["hoy", "today"]:
            start_time = datetime.now() - timedelta(days=1)
            break
        elif start_input.lower() in ["ayer", "yesterday"]:
            start_time = datetime.now() - timedelta(days=2)
            break
        elif start_input.lower() in ["semana", "week"]:
            start_time = datetime.now() - timedelta(weeks=1)
            break
        else:
            try:
                # Intentar parsear fecha personalizada
                if len(start_input) == 10:  # Solo fecha
                    start_time = datetime.strptime(start_input, "%Y-%m-%d")
                else:  # Fecha y hora
                    start_time = datetime.strptime(start_input, "%Y-%m-%d %H:%M")
                break
            except ValueError:
                print("❌ Formato de fecha inválido. Intenta de nuevo.")

    # Fecha fin
    while True:
        end_input = input("🕐 Fecha/hora fin (presiona Enter para 'ahora'): ").strip()

        if not end_input:
            end_time = datetime.now()
            break
        else:
            try:
                if len(end_input) == 10:  # Solo fecha
                    end_time = datetime.strptime(end_input, "%Y-%m-%d")
                    end_time = end_time.replace(
                        hour=23, minute=59, second=59
                    )  # Final del día
                else:  # Fecha y hora
                    end_time = datetime.strptime(end_input, "%Y-%m-%d %H:%M")
                break
            except ValueError:
                print("❌ Formato de fecha inválido. Intenta de nuevo.")

    return start_time, end_time


def seleccionar_bomba(bombas):
    """Permitir al usuario seleccionar una bomba"""
    print(f"\n📋 BOMBAS DISPONIBLES ({len(bombas)} total):")

    # Mostrar primeras 10 bombas
    for i, bomba in enumerate(bombas[:10], 1):
        name = bomba.get("name", "Sin nombre")
        bomba_id = bomba.get("id", "Sin ID")
        print(f"   {i}. {name} (ID: {bomba_id[:8]}...)")

    if len(bombas) > 10:
        print(f"   ... y {len(bombas) - 10} bombas más")

    while True:
        try:
            opcion = input(f"\nSelecciona bomba (1-{min(10, len(bombas))}): ").strip()
            indice = int(opcion) - 1
            if 0 <= indice < min(10, len(bombas)):
                return bombas[indice]
            else:
                print("❌ Número inválido")
        except ValueError:
            print("❌ Ingresa un número válido")


def main():
    print("=" * 60)
    print("🚀 CONSULTA SIMPLE - AQUAADVANCED API")
    print("=" * 60)

    # Modo demo automático si se pasa argumento
    modo_demo = len(sys.argv) > 1 and sys.argv[1] == "demo"
    if modo_demo:
        print("🎬 MODO DEMOSTRACIÓN AUTOMÁTICA")
        print("=" * 60)

    # Inicializar cliente
    print("\n1. 🔧 Inicializando cliente...")
    client = AquaAdvancedClient()

    # Obtener bombas
    print("\n2. 📋 Obteniendo lista de bombas...")
    bombas = client.get_bombas_list()

    if not bombas:
        print("❌ No se pudieron obtener las bombas")
        return

    print(f"✅ {len(bombas)} bombas encontradas")

    # Seleccionar bomba
    if modo_demo:
        bomba_seleccionada = bombas[0]  # Primera bomba para demo
        print(f"🎬 Demo: Seleccionando automáticamente bomba 1")
    else:
        bomba_seleccionada = seleccionar_bomba(bombas)

    bomba_id = bomba_seleccionada["id"]
    bomba_name = bomba_seleccionada.get("name", "Sin nombre")

    print(f"\n✅ Bomba seleccionada: {bomba_name}")
    print(f"   ID: {bomba_id}")

    # Seleccionar endpoint
    endpoints_disponibles = mostrar_menu_endpoints()

    if modo_demo:
        # En modo demo, usar "all_basic"
        _, endpoint_name, endpoint_desc = endpoints_disponibles[12]  # all_basic
        print(f"🎬 Demo: Seleccionando automáticamente 'all_basic'")
    else:
        while True:
            try:
                opcion = input(
                    f"\nSelecciona endpoint (1-{len(endpoints_disponibles)}): "
                ).strip()
                indice = int(opcion) - 1
                if 0 <= indice < len(endpoints_disponibles):
                    _, endpoint_name, endpoint_desc = endpoints_disponibles[indice]
                    break
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Ingresa un número válido")

    print(f"\n✅ Endpoint seleccionado: {endpoint_name} - {endpoint_desc}")

    # Obtener fechas
    if modo_demo:
        # En modo demo, usar últimas 24 horas
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        print(f"🎬 Demo: Usando últimas 24 horas automáticamente")
    else:
        start_time, end_time = obtener_fechas()

    start_iso = start_time.isoformat()
    end_iso = end_time.isoformat()

    print(f"\n✅ Rango de fechas:")
    print(f"   Desde: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Hasta: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Realizar consulta
    print(f"\n🔍 Consultando {endpoint_name}...")

    # Mapear endpoints a métodos del cliente
    endpoint_methods = {
        "status": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_status": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        "power": lambda: client.get_bomba_power(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_power": lambda: client.get_bomba_power(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        "speed": lambda: client.get_bomba_speed(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_speed": lambda: client.get_bomba_speed(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        "onoffschedule": lambda: client.get_bomba_onoffschedule(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_onoffschedule": lambda: client.get_bomba_onoffschedule(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        # Usar los métodos existentes para otros endpoints (usando href dinámico)
        "faults": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_faults": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        "control": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_control": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=True
        ),
        "inservice": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=False
        ),
        "detailed_inservice": lambda: client.get_bomba_status(
            bomba_id, start_iso, end_iso, detailed=True
        ),
    }

    try:
        # Manejar consultas múltiples
        if endpoint_name == "all_basic":
            print("🔄 Consultando todos los endpoints básicos...")
            datos = {}
            for ep in ["status", "power", "speed"]:
                print(f"   • Consultando {ep}...")
                datos[ep] = endpoint_methods[ep]()
        elif endpoint_name == "all_detailed":
            print("🔄 Consultando todos los endpoints detallados...")
            datos = {}
            for ep in ["detailed_status", "detailed_power", "detailed_speed"]:
                print(f"   • Consultando {ep}...")
                datos[ep] = endpoint_methods[ep]()
        elif endpoint_name in endpoint_methods:
            datos = endpoint_methods[endpoint_name]()
        else:
            print(f"⚠️ Endpoint {endpoint_name} no implementado aún")
            return

        # Mostrar resultados
        print(f"\n📊 RESULTADOS:")
        print(f"   Bomba: {bomba_name}")
        print(f"   Endpoint: {endpoint_name}")
        print(
            f"   Rango: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%Y-%m-%d %H:%M')}"
        )

        # Manejar resultados múltiples
        if endpoint_name in ["all_basic", "all_detailed"] and isinstance(datos, dict):
            print(f"   📈 Resumen de consultas múltiples:")
            total_puntos = 0
            for ep_name, ep_data in datos.items():
                if isinstance(ep_data, list):
                    puntos = len(ep_data)
                    total_puntos += puntos
                    status = f"{puntos} puntos" if puntos > 0 else "sin datos"
                    print(f"      • {ep_name}: {status}")
                else:
                    print(
                        f"      • {ep_name}: {type(ep_data)} - {len(ep_data) if hasattr(ep_data, '__len__') else 'N/A'}"
                    )
            print(f"   📊 Total puntos de datos: {total_puntos}")
        elif isinstance(datos, list):
            print(f"   📈 Puntos de datos obtenidos: {len(datos)}")
            if datos:
                print(f"   📋 Muestra de primeros 3 registros:")
                for i, registro in enumerate(datos[:3], 1):
                    print(f"      {i}. {registro}")
            else:
                print("   ℹ️ No hay datos para el rango especificado")
        elif isinstance(datos, dict):
            print(f"   📋 Datos obtenidos (dict con {len(datos)} claves)")
            print(f"   🔍 Claves: {list(datos.keys())}")
        else:
            print(f"   ⚠️ Respuesta: {type(datos)} - {datos}")

        # Preguntar si guardar
        if modo_demo:
            print(f"\n🎬 Demo: Guardando resultados automáticamente...")
            guardar = "s"
        else:
            guardar = (
                input(f"\n💾 ¿Guardar resultados en archivo? (s/N): ").strip().lower()
            )

        if guardar in ["s", "si", "y", "yes"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"consulta_{endpoint_name}_{bomba_name.replace(' ', '_')}_{timestamp}.json"

            resultado = {
                "bomba": {"id": bomba_id, "name": bomba_name},
                "endpoint": endpoint_name,
                "rango": {"inicio": start_iso, "fin": end_iso},
                "datos": datos,
                "timestamp_consulta": datetime.now().isoformat(),
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)

            print(f"✅ Resultados guardados en: {filename}")

    except Exception as e:
        print(f"❌ Error en la consulta: {e}")

    print(f"\n🎉 ¡Consulta completada!")


if __name__ == "__main__":
    main()
