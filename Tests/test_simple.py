#!/usr/bin/env python3
"""
Test simple del API Client de AquaAdvanced
"""

import os
import sys

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aquadapt_api_client_oficial_v2 import AquaAdvancedClient


def main():
    print("=== TEST SIMPLE AQUAADVANCED API ===")

    # Crear cliente
    client = AquaAdvancedClient()

    # Obtener lista de bombas
    print("\n1. Obteniendo lista de bombas...")
    bombas = client.get_bombas_list()

    if bombas:
        print(f"✅ Encontradas {len(bombas)} bombas")

        # Mostrar primeras 3 bombas
        print("\n📋 Primeras 3 bombas:")
        for i, bomba in enumerate(bombas[:3], 1):
            name = bomba.get("name", "Sin nombre")
            bomba_id = bomba.get("id", "Sin ID")
            print(f"   {i}. {name} (ID: {bomba_id[:8]}...)")

        # Probar información detallada de la primera bomba
        print(f"\n2. Información detallada de: {bombas[0].get('name')}")
        info = client.get_bomba_info(bombas[0]["id"])

        if info:
            print(f"✅ Nombre: {info.get('name', 'N/A')}")
            endpoints = [
                k for k, v in info.items() if isinstance(v, dict) and "href" in v
            ]
            print(f"✅ Endpoints disponibles: {len(endpoints)}")
        else:
            print("❌ No se pudo obtener información detallada")

    else:
        print("❌ No se pudieron obtener las bombas")

    print("\n✅ Test completado")


if __name__ == "__main__":
    main()
