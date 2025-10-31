#!/usr/bin/env python3
"""
Ejemplos de uso del cliente oficial de AquaAdvanced API
Basado en la documentación oficial de la API
"""

import json
import sys
from datetime import datetime, timedelta
from aquadapt_api_client_oficial import AquaAdvancedClient
import config

def mostrar_menu():
    """Muestra el menú principal de opciones."""
    print("\n" + "="*60)
    print("     CLIENTE API AQUAADVANCED - MENÚ PRINCIPAL")
    print("="*60)
    print("1. Probar conexión")
    print("2. Listar todas las bombas") 
    print("3. Consultar bomba específica")
    print("4. Obtener estado de bomba")
    print("5. Obtener potencia de bomba")
    print("6. Obtener velocidad de bomba")
    print("7. Obtener fallos de bomba")
    print("8. Obtener todos los datos de una bomba")
    print("9. Monitoreo en tiempo real")
    print("10. Exportar datos históricos")
    print("11. Ver configuración actual")
    print("0. Salir")
    print("="*60)

def probar_conexion(client):
    """Prueba la conexión con la API."""
    print("\n🔍 Probando conexión con la API...")
    
    if client.test_connection():
        print("✅ ¡Conexión exitosa!")
        print(f"   URL: {client.base_url}")
        print(f"   Método auth: {client.auth_method}")
        return True
    else:
        print("❌ Error de conexión")
        print("   Verifica la configuración en config.py")
        return False

def listar_bombas(client):
    """Lista todas las bombas disponibles."""
    print("\n📋 Obteniendo lista de bombas...")
    
    try:
        bombas = client.get_bombas_list()
        
        if not bombas:
            print("❌ No se encontraron bombas")
            return []
        
        print(f"✅ Encontradas {len(bombas)} bombas:")
        print("-" * 80)
        print(f"{'ID':<40} {'Nombre':<30} {'Tipo'}")
        print("-" * 80)
        
        for bomba in bombas:
            bomba_id = bomba.get('id', 'N/A')[:38]
            nombre = bomba.get('name', 'Sin nombre')[:28]
            tipo = bomba.get('type', 'Physical Pump')
            print(f"{bomba_id:<40} {nombre:<30} {tipo}")
        
        return bombas
        
    except Exception as e:
        print(f"❌ Error al obtener bombas: {e}")
        return []

def consultar_bomba_especifica(client):
    """Consulta información específica de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    print(f"\n📋 Consultando bomba {bomba_id}...")
    
    try:
        info = client.get_bomba_info(bomba_id)
        
        if info:
            print("✅ Información de la bomba:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print("❌ No se encontró información de la bomba")
            
    except Exception as e:
        print(f"❌ Error al consultar bomba: {e}")

def obtener_estado_bomba(client):
    """Obtiene el estado de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    detallado = input("¿Usar endpoint detallado? (s/N): ").strip().lower() == 's'
    
    print(f"\n⚡ Obteniendo estado de bomba {bomba_id}...")
    
    try:
        status = client.get_bomba_status(bomba_id, detailed=detallado)
        
        if status:
            print("✅ Estado de la bomba:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print("❌ No se pudo obtener el estado")
            
    except Exception as e:
        print(f"❌ Error al obtener estado: {e}")

def obtener_potencia_bomba(client):
    """Obtiene la potencia de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    detallado = input("¿Usar endpoint detallado? (s/N): ").strip().lower() == 's'
    
    print(f"\n⚡ Obteniendo potencia de bomba {bomba_id}...")
    
    try:
        power = client.get_bomba_power(bomba_id, detailed=detallado)
        
        if power:
            print("✅ Potencia de la bomba:")
            print(json.dumps(power, indent=2, ensure_ascii=False))
        else:
            print("❌ No se pudo obtener la potencia")
            
    except Exception as e:
        print(f"❌ Error al obtener potencia: {e}")

def obtener_velocidad_bomba(client):
    """Obtiene la velocidad de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    detallado = input("¿Usar endpoint detallado? (s/N): ").strip().lower() == 's'
    
    print(f"\n🚀 Obteniendo velocidad de bomba {bomba_id}...")
    
    try:
        speed = client.get_bomba_speed(bomba_id, detailed=detallado)
        
        if speed:
            print("✅ Velocidad de la bomba:")
            print(json.dumps(speed, indent=2, ensure_ascii=False))
        else:
            print("❌ No se pudo obtener la velocidad")
            
    except Exception as e:
        print(f"❌ Error al obtener velocidad: {e}")

def obtener_fallos_bomba(client):
    """Obtiene los fallos de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    detallado = input("¿Usar endpoint detallado? (s/N): ").strip().lower() == 's'
    
    print(f"\n⚠️ Obteniendo fallos de bomba {bomba_id}...")
    
    try:
        faults = client.get_bomba_faults(bomba_id, detailed=detallado)
        
        if faults:
            print("✅ Fallos de la bomba:")
            print(json.dumps(faults, indent=2, ensure_ascii=False))
        else:
            print("❌ No se pudieron obtener los fallos")
            
    except Exception as e:
        print(f"❌ Error al obtener fallos: {e}")

def obtener_todos_datos_bomba(client):
    """Obtiene todos los datos disponibles de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    detallado = input("¿Usar endpoints detallados? (s/N): ").strip().lower() == 's'
    
    print(f"\n📊 Obteniendo todos los datos de bomba {bomba_id}...")
    
    try:
        all_data = client.get_all_bomba_data(bomba_id, detailed=detallado)
        
        if all_data:
            print("✅ Datos completos de la bomba:")
            print(json.dumps(all_data, indent=2, ensure_ascii=False))
            
            # Opción de guardar en archivo
            guardar = input("\n¿Guardar datos en archivo? (s/N): ").strip().lower() == 's'
            if guardar:
                filename = f"bomba_{bomba_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Datos guardados en {filename}")
        else:
            print("❌ No se pudieron obtener los datos")
            
    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")

def monitoreo_tiempo_real(client):
    """Realiza monitoreo básico en tiempo real."""
    print("\n📡 Iniciando monitoreo básico...")
    
    # Obtener lista de bombas primero
    bombas = client.get_bombas_list()
    if not bombas:
        print("❌ No se pueden obtener bombas para monitorear")
        return
    
    print(f"Monitoreando {len(bombas)} bombas")
    print("Presiona Ctrl+C para detener el monitoreo")
    
    try:
        import time
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            for i, bomba in enumerate(bombas[:5]):  # Solo primeras 5 para no saturar
                bomba_id = bomba.get('id', '')
                nombre = bomba.get('name', 'Sin nombre')
                
                try:
                    status = client.get_bomba_status(bomba_id)
                    if status and isinstance(status, list) and len(status) > 0:
                        ultimo_status = status[-1] if isinstance(status, list) else status
                        valor = ultimo_status.get('value', 'N/A')
                        tiempo = ultimo_status.get('time', 'N/A')
                        print(f"{nombre[:20]:<20} | Estado: {valor} | {tiempo}")
                    else:
                        print(f"{nombre[:20]:<20} | Estado: Sin datos")
                except:
                    print(f"{nombre[:20]:<20} | Estado: Error")
            
            time.sleep(30)  # Esperar 30 segundos
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo detenido por el usuario")

def exportar_datos_historicos(client):
    """Exporta datos históricos de una bomba."""
    bomba_id = input("\n🔍 Ingresa el ID de la bomba: ").strip()
    
    if not bomba_id:
        print("❌ ID de bomba requerido")
        return
    
    print("\n📅 Configurar periodo de tiempo:")
    horas = input("Horas hacia atrás (por defecto 24): ").strip()
    
    try:
        horas = int(horas) if horas else 24
    except ValueError:
        horas = 24
    
    # Calcular tiempos
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=horas)
    
    print(f"\n📤 Exportando datos históricos de {horas} horas...")
    print(f"   Desde: {start_time.isoformat()}")
    print(f"   Hasta: {end_time.isoformat()}")
    
    try:
        data_historica = {
            'bomba_id': bomba_id,
            'periodo': {
                'inicio': start_time.isoformat(),
                'fin': end_time.isoformat(),
                'horas': horas
            },
            'datos': {}
        }
        
        # Obtener diferentes tipos de datos históricos
        tipos_datos = ['status', 'power', 'speed', 'faults']
        
        for tipo in tipos_datos:
            print(f"   Obteniendo {tipo}...")
            
            if tipo == 'status':
                datos = client.get_bomba_status(bomba_id, start_time.isoformat(), 
                                              end_time.isoformat(), detailed=True)
            elif tipo == 'power':
                datos = client.get_bomba_power(bomba_id, start_time.isoformat(),
                                             end_time.isoformat(), detailed=True)
            elif tipo == 'speed':
                datos = client.get_bomba_speed(bomba_id, start_time.isoformat(),
                                             end_time.isoformat(), detailed=True)
            elif tipo == 'faults':
                datos = client.get_bomba_faults(bomba_id, start_time.isoformat(),
                                              end_time.isoformat(), detailed=True)
            
            data_historica['datos'][tipo] = datos
        
        # Guardar archivo
        filename = f"historicos_bomba_{bomba_id}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_historica, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos históricos exportados a {filename}")
        
    except Exception as e:
        print(f"❌ Error al exportar datos: {e}")

def ver_configuracion():
    """Muestra la configuración actual."""
    print("\n⚙️ Configuración actual:")
    print("-" * 50)
    print(f"URL Base: {config.API_BASE_URL}")
    print(f"Verificar SSL: {config.VERIFY_SSL}")
    print(f"Timeout: {config.TIMEOUT}s")
    print(f"Reintentos: {config.RETRY_COUNT}")
    print(f"Nivel de log: {config.LOG_LEVEL}")
    
    # Mostrar método de autenticación sin exponer credenciales
    if hasattr(config, 'API_KEY') and config.API_KEY:
        print(f"Autenticación: API Key configurada")
    elif config.USERNAME and config.PASSWORD:
        print(f"Autenticación: Usuario/contraseña configurada")
    else:
        print(f"Autenticación: ❌ Sin configurar")
    
    print(f"\nEndpoints disponibles:")
    for key, endpoint in config.ENDPOINTS.items():
        print(f"  {key}: {endpoint}")

def main():
    """Función principal del programa."""
    print("🚀 Iniciando cliente API AquaAdvanced...")
    
    # Crear cliente
    try:
        client = AquaAdvancedClient()
    except Exception as e:
        print(f"❌ Error al crear cliente: {e}")
        return
    
    # Menú principal
    while True:
        try:
            mostrar_menu()
            opcion = input("\n➤ Selecciona una opción: ").strip()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            elif opcion == '1':
                probar_conexion(client)
            elif opcion == '2':
                listar_bombas(client)
            elif opcion == '3':
                consultar_bomba_especifica(client)
            elif opcion == '4':
                obtener_estado_bomba(client)
            elif opcion == '5':
                obtener_potencia_bomba(client)
            elif opcion == '6':
                obtener_velocidad_bomba(client)
            elif opcion == '7':
                obtener_fallos_bomba(client)
            elif opcion == '8':
                obtener_todos_datos_bomba(client)
            elif opcion == '9':
                monitoreo_tiempo_real(client)
            elif opcion == '10':
                exportar_datos_historicos(client)
            elif opcion == '11':
                ver_configuracion()
            else:
                print("❌ Opción no válida")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")

if __name__ == '__main__':
    main()