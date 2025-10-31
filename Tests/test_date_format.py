#!/usr/bin/env python3
"""
Test para validar el formato de fechas para la API AquaAdvanced
"""

import os
import sys
from datetime import datetime, timedelta

# Añadir directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aquadapt_api_client_oficial_v2 import AquaAdvancedClient


def test_date_formatting():
    """Probar diferentes formatos de fecha"""
    print("🔍 PRUEBA DE FORMATO DE FECHAS PARA API AQUAADVANCED")
    print("=" * 60)

    client = AquaAdvancedClient()

    # Casos de prueba
    test_cases = [
        # Fecha ISO básica
        "2025-10-22T00:00:00",
        # Fecha ISO con microsegundos
        "2025-10-22T14:30:45.123456",
        # Fecha ISO ya con Z
        "2025-10-22T00:00:00Z",
        # Fecha de ejemplo del usuario
        "2025-10-22T00:00:00",
        # Fechas actuales
        datetime.now().isoformat(),
        (datetime.now() - timedelta(days=1)).isoformat(),
    ]

    print("📅 Probando conversión de formatos de fecha:\n")

    for i, test_date in enumerate(test_cases, 1):
        print(f"{i}. Fecha entrada: {test_date}")
        try:
            formatted = client._format_datetime_for_api(str(test_date))
            print(f"   Fecha API:     {formatted}")

            # Verificar que tenga el formato esperado
            if "%3A" in formatted and formatted.endswith("Z"):
                print("   ✅ Formato correcto")
            else:
                print("   ❌ Formato incorrecto")

        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

    print("🎯 FORMATO ESPERADO PARA LA API:")
    print("   Ejemplo: 2025-10-22T00%3A00%3A00Z")
    print("   - Los dos puntos (:) se codifican como %3A")
    print("   - Debe terminar con Z para indicar UTC")

    # Probar con fechas del main.py
    print("\n🔬 PRUEBA CON FECHAS DEL SISTEMA:")
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    print(f"Ahora (sistema):     {now.isoformat()}")
    print(f"Ahora (API):         {client._format_datetime_for_api(now.isoformat())}")
    print(f"Ayer (sistema):      {yesterday.isoformat()}")
    print(
        f"Ayer (API):          {client._format_datetime_for_api(yesterday.isoformat())}"
    )


if __name__ == "__main__":
    test_date_formatting()
