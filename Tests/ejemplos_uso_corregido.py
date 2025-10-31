#!/usr/bin/env python3
"""
Ejemplo de uso del cliente AquaAdvanced API - Versión Corregida
Muestra diferentes formas de consultar y usar los datos
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aquadapt_api_client_oficial_v2 import AquaAdvancedClient, load_bmb_list_from_file
import config

# Importar pandas solo si está disponible
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def ejemplo_consulta_individual():
    """Ejemplo: consultar datos de una bomba específica"""
    print("=== Consulta Individual ===")
    
    # Crear cliente (usa config.py automáticamente)
    client = AquaAdvancedClient()
    
    # Obtener lista de bombas (desde API o archivo local)
    bmb_list = client.get_bombas_list()
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Seleccionar primera bomba como ejemplo
    first_bmb = bmb_list[0]
    bmb_id = first_bmb['id']
    bmb_name = first_bmb.get('name', 'Sin nombre')
    
    print(f"Consultando bomba: {bmb_name} (ID: {bmb_id})")
    
    # Primero obtener información básica de la bomba
    info = client.get_bomba_info(bmb_id)
    print(f"Información básica: {info}")
    
    # Para datos temporales, necesitamos especificar rangos de tiempo
    from datetime import timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)  # Último día
    
    start_iso = start_time.isoformat()
    end_iso = end_time.isoformat()
    
    print(f"Consultando datos desde {start_time.strftime('%Y-%m-%d %H:%M')} hasta {end_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Obtener datos con rangos de tiempo
    status = client.get_bomba_status(bmb_id, start_iso, end_iso)
    power = client.get_bomba_power(bmb_id, start_iso, end_iso)
    speed = client.get_bomba_speed(bmb_id, start_iso, end_iso)
    
    print(f"Estado: {len(status) if status else 0} puntos de datos")
    print(f"Potencia: {len(power) if power else 0} puntos de datos")
    print(f"Velocidad: {len(speed) if speed else 0} puntos de datos")

def ejemplo_monitoreo_multiples():
    """Ejemplo: monitorear múltiples bombas específicas"""
    print("=== Monitoreo Múltiples Bombas ===")
    
    client = AquaAdvancedClient()
    bmb_list = client.get_bombas_list()
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Filtrar bombas específicas (ej: solo EB0, EB3, EB10)
    bombas_interes = ["EB0", "EB3", "EB10"]
    bombas_filtradas = [
        bmb for bmb in bmb_list 
        if any(interes in bmb.get('name', '') for interes in bombas_interes)
    ]
    
    print(f"Monitoreando {len(bombas_filtradas)} bombas:")
    
    for bmb in bombas_filtradas:
        print(f"  - {bmb.get('name', 'Sin nombre')} (ID: {bmb['id']})")
        
        # Obtener solo estado y fallos para monitoreo rápido
        status = client.get_bomba_status(bmb['id'])
        faults = client.get_bomba_faults(bmb['id'])
        
        if faults:
            print(f"    ⚠️  ALERTA: Fallos detectados")
        else:
            print(f"    ✅ Sin fallos")

def ejemplo_reporte_completo():
    """Ejemplo: generar reporte completo de todas las bombas"""
    print("=== Reporte Completo ===")
    
    client = AquaAdvancedClient()
    bmb_list = client.get_bombas_list()
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Generar reporte resumen
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_bombas': len(bmb_list),
        'bombas_procesadas': 0,
        'bombas_con_fallos': 0,
        'resumen_por_bomba': []
    }
    
    # Procesar solo primeras 5 bombas para ejemplo
    for bmb in bmb_list[:5]:
        bmb_id = bmb['id']
        bmb_name = bmb.get('name', 'Sin nombre')
        
        print(f"Procesando {bmb_name}...")
        
        # Obtener datos básicos
        status = client.get_bomba_status(bmb_id)
        faults = client.get_bomba_faults(bmb_id)
        power = client.get_bomba_power(bmb_id)
        
        has_faults = bool(faults)
        if has_faults:
            report['bombas_con_fallos'] += 1
        
        report['resumen_por_bomba'].append({
            'id': bmb_id,
            'name': bmb_name,
            'has_faults': has_faults,
            'status_available': status is not None,
            'power_available': power is not None
        })
        
        report['bombas_procesadas'] += 1
    
    # Guardar reporte
    filename = f'reporte_resumen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Reporte generado: {filename}")
    print(f"  Total bombas: {report['total_bombas']}")
    print(f"  Bombas procesadas: {report['bombas_procesadas']}")
    print(f"  Bombas con fallos: {report['bombas_con_fallos']}")

def ejemplo_exportar_csv():
    """Ejemplo: exportar datos a CSV para análisis"""
    print("=== Exportar a CSV ===")
    
    if not PANDAS_AVAILABLE:
        print("pandas no está instalado. Instálalo con: pip install pandas")
        return
    
    client = AquaAdvancedClient()
    bmb_list = client.get_bombas_list()
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Preparar datos para DataFrame
    data_for_df = []
    
    for bmb in bmb_list[:5]:  # Solo primeras 5 para ejemplo
        bmb_id = bmb['id']
        bmb_name = bmb.get('name', 'Sin nombre')
        
        print(f"Procesando {bmb_name} para CSV...")
        
        # Obtener datos básicos
        status = client.get_bomba_status(bmb_id)
        power = client.get_bomba_power(bmb_id)
        
        row = {
            'ID': bmb_id,
            'Nombre': bmb_name,
            'Timestamp': datetime.now(),
            'Estado_Disponible': status is not None,
            'Potencia_Disponible': power is not None
        }
        
        # Agregar campos específicos si los datos están disponibles
        if status and isinstance(status, list) and len(status) > 0:
            # Usar el último valor si es una lista
            ultimo_status = status[-1] if isinstance(status, list) else status
            row.update({
                'Estado_Valor': ultimo_status.get('value', 'N/A'),
                'Estado_Tiempo': ultimo_status.get('time', 'N/A')
            })
        
        if power and isinstance(power, list) and len(power) > 0:
            ultimo_power = power[-1] if isinstance(power, list) else power
            row.update({
                'Potencia_Valor': ultimo_power.get('value', 'N/A'),
                'Potencia_Tiempo': ultimo_power.get('time', 'N/A')
            })
        
        data_for_df.append(row)
    
    # Crear DataFrame y exportar
    try:
        df = pd.DataFrame(data_for_df)
        csv_filename = f"bombas_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Datos exportados a {csv_filename}")
        print("\nPrimeras filas del CSV:")
        print(df.head())
    except Exception as e:
        print(f"Error al exportar CSV: {e}")

def ejemplo_consulta_tiempo_real():
    """Ejemplo: consulta en tiempo real con intervalos"""
    print("=== Consulta Tiempo Real ===")
    import time
    
    client = AquaAdvancedClient()
    bmb_list = client.get_bombas_list()
    
    # Seleccionar una bomba para monitoreo
    if not bmb_list:
        print("No hay bombas disponibles")
        return
    
    bmb = bmb_list[0]  # Primera bomba
    bmb_id = bmb['id']
    bmb_name = bmb.get('name', 'Sin nombre')
    
    print(f"Monitoreando bomba {bmb_name} cada 10 segundos...")
    print("Presiona Ctrl+C para detener")
    
    try:
        for i in range(6):  # 6 iteraciones = 1 minuto
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            status = client.get_bomba_status(bmb_id)
            power = client.get_bomba_power(bmb_id)
            
            print(f"[{timestamp}] {bmb_name}:")
            print(f"  Estado: {'OK' if status else 'Error'}")
            print(f"  Potencia: {'OK' if power else 'Error'}")
            
            if i < 5:  # No esperar en la última iteración
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")

def ejemplo_datos_detallados():
    """Ejemplo: obtener datos detallados de una bomba"""
    print("=== Datos Detallados ===")
    
    client = AquaAdvancedClient()
    bmb_list = client.get_bombas_list()
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Seleccionar primera bomba
    bmb = bmb_list[0]
    bmb_id = bmb['id']
    bmb_name = bmb.get('name', 'Sin nombre')
    
    print(f"Obteniendo datos detallados de: {bmb_name}")
    
    # Obtener todos los datos disponibles
    all_data = client.get_all_bomba_data(bmb_id, detailed=True)
    
    if all_data:
        # Guardar en archivo
        filename = f"datos_detallados_{bmb_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"Datos guardados en: {filename}")
        print("\nResumen de datos obtenidos:")
        for key, value in all_data.items():
            if key != 'bomba_id' and key != 'timestamp':
                data_available = value is not None and value != {}
                print(f"  {key}: {'✅' if data_available else '❌'}")
    else:
        print("No se pudieron obtener datos detallados")

def main():
    """Menú principal de ejemplos"""
    ejemplos = {
        '1': ('Consulta Individual', ejemplo_consulta_individual),
        '2': ('Monitoreo Múltiples', ejemplo_monitoreo_multiples),
        '3': ('Reporte Completo', ejemplo_reporte_completo),
        '4': ('Exportar CSV', ejemplo_exportar_csv),
        '5': ('Tiempo Real', ejemplo_consulta_tiempo_real),
        '6': ('Datos Detallados', ejemplo_datos_detallados)
    }
    
    print("=== Ejemplos de uso AquaAdvanced API ===")
    print("Selecciona un ejemplo:")
    
    for key, (description, _) in ejemplos.items():
        print(f"{key}. {description}")
    
    print("0. Salir")
    
    choice = input("\nIngresa tu opción: ").strip()
    
    if choice == '0':
        print("¡Hasta luego!")
        return
    
    if choice in ejemplos:
        _, func = ejemplos[choice]
        print(f"\nEjecutando: {ejemplos[choice][0]}")
        print("-" * 50)
        try:
            func()
        except Exception as e:
            print(f"Error ejecutando ejemplo: {e}")
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()