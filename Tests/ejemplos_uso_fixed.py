#!/usr/bin/env python3
"""
Ejemplo de uso del cliente AquaAdvanced API
Muestra diferentes formas de consultar y usar los datos
"""

import sys
import os
from datetime import datetime

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aquadapt_api_client import AquaAdvancedClient, load_bmb_list_from_file
import config

def ejemplo_consulta_individual():
    """Ejemplo: consultar datos de una bomba específica"""
    print("=== Consulta Individual ===")
    
    client = AquaAdvancedClient(base_url=config.API_BASE_URL, verify_ssl=config.VERIFY_SSL)
    
    # Cargar lista de bombas
    bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)
    
    if not bmb_list:
        print("No se pudo cargar la lista de bombas")
        return
    
    # Seleccionar primera bomba como ejemplo
    first_bmb = bmb_list[0]
    bmb_id = first_bmb['id']
    bmb_name = first_bmb['name']
    
    print(f"Consultando bomba: {bmb_name} (ID: {bmb_id})")
    
    # Obtener datos
    status = client.get_bmb_status(bmb_id)
    power = client.get_bmb_power(bmb_id)
    speed = client.get_bmb_speed(bmb_id)
    
    print(f"Estado: {status}")
    print(f"Potencia: {power}")
    print(f"Velocidad: {speed}")

def ejemplo_monitoreo_multiples():
    """Ejemplo: monitorear múltiples bombas específicas"""
    print("=== Monitoreo Múltiples Bombas ===")
    
    client = AquaAdvancedClient(base_url=config.API_BASE_URL, verify_ssl=config.VERIFY_SSL)
    bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)
    
    # Filtrar bombas específicas (ej: solo EB0, EB3, EB10)
    bombas_interes = ["EB0", "EB3", "EB10"]
    bombas_filtradas = [
        bmb for bmb in bmb_list 
        if any(interes in bmb['name'] for interes in bombas_interes)
    ]
    
    print(f"Monitoreando {len(bombas_filtradas)} bombas:")
    
    for bmb in bombas_filtradas:
        print(f"  - {bmb['name']} (ID: {bmb['id']})")
        
        # Obtener solo estado y fallos para monitoreo rápido
        status = client.get_bmb_status(bmb['id'])
        faults = client.get_bmb_faults(bmb['id'])
        
        if faults:
            print(f"    ⚠️  ALERTA: Fallos detectados")
        else:
            print(f"    ✅ Sin fallos")

def ejemplo_reporte_completo():
    """Ejemplo: generar reporte completo de todas las bombas"""
    print("=== Reporte Completo ===")
    
    client = AquaAdvancedClient(base_url=config.API_BASE_URL, verify_ssl=config.VERIFY_SSL)
    bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)
    
    # Obtener datos completos
    all_data = client.get_all_bmb_data(bmb_list)
    
    # Generar reporte resumen
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_bombas': len(all_data),
        'bombas_con_fallos': 0,
        'bombas_activas': 0,
        'resumen_por_bomba': []
    }
    
    for bmb_id, data in all_data.items():
        bmb_info = data['basic_info']
        has_faults = bool(data.get('faults'))
        
        if has_faults:
            report['bombas_con_fallos'] += 1
        
        # Aquí podrías analizar el estado para determinar si está activa
        # Dependería de la estructura específica de los datos de estado
        
        report['resumen_por_bomba'].append({
            'id': bmb_id,
            'name': bmb_info.get('name', 'N/A'),
            'has_faults': has_faults,
            'status_available': data.get('status') is not None,
            'power_available': data.get('power') is not None
        })
    
    # Guardar reporte
    client.save_data_to_file(report, 'reporte_resumen.json')
    
    print(f"Reporte generado:")
    print(f"  Total bombas: {report['total_bombas']}")
    print(f"  Bombas con fallos: {report['bombas_con_fallos']}")

def ejemplo_exportar_csv():
    """Ejemplo: exportar datos a CSV para análisis"""
    print("=== Exportar a CSV ===")
    
    client = AquaAdvancedClient(base_url=config.API_BASE_URL, verify_ssl=config.VERIFY_SSL)
    bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)
    
    # Preparar datos para DataFrame
    data_for_df = []
    
    for bmb in bmb_list[:5]:  # Solo primeras 5 para ejemplo
        bmb_id = bmb['id']
        bmb_name = bmb['name']
        
        # Obtener datos básicos
        status = client.get_bmb_status(bmb_id)
        power = client.get_bmb_power(bmb_id)
        
        row = {
            'ID': bmb_id,
            'Nombre': bmb_name,
            'Timestamp': datetime.now(),
            'Estado_Disponible': status is not None,
            'Potencia_Disponible': power is not None
        }
        
        # Agregar campos específicos si los datos están disponibles
        if status:
            # Ajustar según la estructura real de los datos
            row.update({
                'Estado': status.get('value', 'N/A'),
                'Estado_Descripcion': status.get('description', 'N/A')
            })
        
        if power:
            row.update({
                'Potencia': power.get('value', 'N/A'),
                'Unidad_Potencia': power.get('unit', 'N/A')
            })
        
        data_for_df.append(row)
    
    # Crear DataFrame y exportar
    try:
        import pandas as pd
        df = pd.DataFrame(data_for_df)
        csv_filename = f"bombas_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"Datos exportados a {csv_filename}")
        print(df.head())
    except ImportError:
        print("pandas no está instalado. Instálalo con: pip install pandas")
        # Alternativa sin pandas - crear CSV manualmente
        import csv
        csv_filename = f"bombas_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if data_for_df:
                fieldnames = data_for_df[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_for_df)
                print(f"Datos exportados a {csv_filename} (sin pandas)")
    except Exception as e:
        print(f"Error al exportar CSV: {e}")

def ejemplo_consulta_tiempo_real():
    """Ejemplo: consulta en tiempo real con intervalos"""
    print("=== Consulta Tiempo Real ===")
    import time
    
    client = AquaAdvancedClient(base_url=config.API_BASE_URL, verify_ssl=config.VERIFY_SSL)
    bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)
    
    # Seleccionar una bomba para monitoreo
    if not bmb_list:
        print("No hay bombas disponibles")
        return
    
    bmb = bmb_list[0]  # Primera bomba
    bmb_id = bmb['id']
    bmb_name = bmb['name']
    
    print(f"Monitoreando bomba {bmb_name} cada 10 segundos...")
    print("Presiona Ctrl+C para detener")
    
    try:
        for i in range(6):  # 6 iteraciones = 1 minuto
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            status = client.get_bmb_status(bmb_id)
            power = client.get_bmb_power(bmb_id)
            
            print(f"[{timestamp}] {bmb_name}:")
            print(f"  Estado: {'OK' if status else 'Error'}")
            print(f"  Potencia: {'OK' if power else 'Error'}")
            
            if i < 5:  # No esperar en la última iteración
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")

def main():
    """Menú principal de ejemplos"""
    ejemplos = {
        '1': ('Consulta Individual', ejemplo_consulta_individual),
        '2': ('Monitoreo Múltiples', ejemplo_monitoreo_multiples),
        '3': ('Reporte Completo', ejemplo_reporte_completo),
        '4': ('Exportar CSV', ejemplo_exportar_csv),
        '5': ('Tiempo Real', ejemplo_consulta_tiempo_real)
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
        func()
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()