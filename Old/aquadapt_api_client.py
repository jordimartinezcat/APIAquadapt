#!/usr/bin/env python3
"""
AquaAdvanced API Client
Script para consultar la API de AquaAdvanced y obtener información de las bombas (BMB)
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Desactivar warnings SSL si es necesario para conexiones locales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AquaAdvancedClient:
    """Cliente para la API de AquaAdvanced"""
    
    def __init__(self, base_url: str = "https://aquadvanced.ccaait.local", 
                 verify_ssl: bool = False, timeout: int = 30):
        """
        Inicializar cliente de API
        
        Args:
            base_url: URL base de la API
            verify_ssl: Verificar certificados SSL
            timeout: Timeout para las peticiones
        """
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()
        
        # Headers por defecto
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'AquaAdvanced-Client/1.0'
        })
    
    def authenticate(self, username: str = None, password: str = None, 
                    token: str = None) -> bool:
        """
        Autenticar con la API
        
        Args:
            username: Usuario
            password: Contraseña
            token: Token de autenticación
            
        Returns:
            bool: True si la autenticación fue exitosa
        """
        try:
            if token:
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                logger.info("Autenticación configurada con token")
                return True
            elif username and password:
                # Implementar autenticación básica o endpoint de login
                # Esto dependerá de la documentación específica de la API
                auth_data = {'username': username, 'password': password}
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json=auth_data,
                    verify=self.verify_ssl,
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    token_data = response.json()
                    if 'token' in token_data:
                        self.session.headers.update({
                            'Authorization': f'Bearer {token_data["token"]}'
                        })
                        logger.info("Autenticación exitosa")
                        return True
                logger.error(f"Error de autenticación: {response.status_code}")
                return False
            else:
                logger.info("Sin autenticación configurada")
                return True
        except Exception as e:
            logger.error(f"Error durante la autenticación: {e}")
            return False
    
    def get_bmb_list(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de todas las bombas (BMB)
        
        Returns:
            List: Lista de bombas con sus datos básicos
        """
        try:
            response = self.session.get(
                f"{self.base_url}/bmb",  # Endpoint a confirmar con la documentación
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            bmb_data = response.json()
            logger.info(f"Obtenidas {len(bmb_data)} bombas")
            return bmb_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener lista de bombas: {e}")
            return []
    
    def get_bmb_status(self, bmb_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estado de una bomba específica
        
        Args:
            bmb_id: ID de la bomba
            
        Returns:
            Dict: Datos del estado de la bomba
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{bmb_id}/status/",
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            status_data = response.json()
            logger.info(f"Estado obtenido para bomba {bmb_id}")
            return status_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener estado de bomba {bmb_id}: {e}")
            return None
    
    def get_bmb_detailed_status(self, bmb_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estado detallado de una bomba específica
        
        Args:
            bmb_id: ID de la bomba
            
        Returns:
            Dict: Datos detallados del estado de la bomba
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{bmb_id}/status/detailed/",
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            detailed_data = response.json()
            logger.info(f"Estado detallado obtenido para bomba {bmb_id}")
            return detailed_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener estado detallado de bomba {bmb_id}: {e}")
            return None
    
    def get_bmb_power(self, bmb_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de potencia de una bomba específica
        
        Args:
            bmb_id: ID de la bomba
            
        Returns:
            Dict: Datos de potencia de la bomba
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{bmb_id}/rawpower/",
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            power_data = response.json()
            logger.info(f"Datos de potencia obtenidos para bomba {bmb_id}")
            return power_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener datos de potencia de bomba {bmb_id}: {e}")
            return None
    
    def get_bmb_speed(self, bmb_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener datos de velocidad de una bomba específica
        
        Args:
            bmb_id: ID de la bomba
            
        Returns:
            Dict: Datos de velocidad de la bomba
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{bmb_id}/speed/",
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            speed_data = response.json()
            logger.info(f"Datos de velocidad obtenidos para bomba {bmb_id}")
            return speed_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener datos de velocidad de bomba {bmb_id}: {e}")
            return None
    
    def get_bmb_faults(self, bmb_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener fallos de una bomba específica
        
        Args:
            bmb_id: ID de la bomba
            
        Returns:
            Dict: Datos de fallos de la bomba
        """
        try:
            response = self.session.get(
                f"{self.base_url}/{bmb_id}/fault/",
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            fault_data = response.json()
            logger.info(f"Datos de fallos obtenidos para bomba {bmb_id}")
            return fault_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener fallos de bomba {bmb_id}: {e}")
            return None
    
    def get_all_bmb_data(self, bmb_list: List[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Obtener todos los datos de todas las bombas
        
        Args:
            bmb_list: Lista de bombas (si no se proporciona, se obtiene automáticamente)
            
        Returns:
            Dict: Diccionario con todos los datos de todas las bombas
        """
        if bmb_list is None:
            bmb_list = self.get_bmb_list()
        
        all_data = {}
        
        for bmb in bmb_list:
            bmb_id = bmb.get('id')
            if not bmb_id:
                continue
                
            logger.info(f"Obteniendo datos para bomba {bmb.get('name', bmb_id)}")
            
            bmb_data = {
                'basic_info': bmb,
                'status': self.get_bmb_status(bmb_id),
                'detailed_status': self.get_bmb_detailed_status(bmb_id),
                'power': self.get_bmb_power(bmb_id),
                'speed': self.get_bmb_speed(bmb_id),
                'faults': self.get_bmb_faults(bmb_id),
                'timestamp': datetime.now().isoformat()
            }
            
            all_data[bmb_id] = bmb_data
        
        return all_data
    
    def save_data_to_file(self, data: Dict[str, Any], filename: str = None):
        """
        Guardar datos en archivo JSON
        
        Args:
            data: Datos a guardar
            filename: Nombre del archivo (opcional)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aquadapt_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Datos guardados en {filename}")
        except Exception as e:
            logger.error(f"Error al guardar datos: {e}")


def load_bmb_list_from_file(filename: str = "aquadapt BMB Id.json") -> List[Dict[str, Any]]:
    """
    Cargar lista de bombas desde archivo JSON local
    
    Args:
        filename: Nombre del archivo JSON
        
    Returns:
        List: Lista de bombas
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            bmb_list = json.load(f)
        logger.info(f"Cargadas {len(bmb_list)} bombas desde {filename}")
        return bmb_list
    except Exception as e:
        logger.error(f"Error al cargar archivo {filename}: {e}")
        return []


def main():
    """Función principal"""
    # Configuración
    API_BASE_URL = "https://aquadvanced.ccaait.local"
    
    # Crear cliente
    client = AquaAdvancedClient(base_url=API_BASE_URL)
    
    # Autenticación (ajustar según sea necesario)
    # client.authenticate(username="usuario", password="contraseña")
    # o
    # client.authenticate(token="tu_token_aqui")
    
    try:
        # Opción 1: Obtener lista desde la API
        logger.info("Obteniendo lista de bombas desde la API...")
        bmb_list = client.get_bmb_list()
        
        # Opción 2: Cargar desde archivo local si la API no funciona
        if not bmb_list:
            logger.info("Cargando lista de bombas desde archivo local...")
            bmb_list = load_bmb_list_from_file()
        
        if not bmb_list:
            logger.error("No se pudo obtener la lista de bombas")
            return
        
        # Obtener todos los datos
        logger.info("Obteniendo datos completos de todas las bombas...")
        all_data = client.get_all_bmb_data(bmb_list)
        
        # Guardar datos
        client.save_data_to_file(all_data)
        
        # Mostrar resumen
        logger.info(f"Proceso completado. Datos obtenidos de {len(all_data)} bombas")
        
        # Ejemplo: mostrar algunas bombas con problemas
        for bmb_id, data in all_data.items():
            if data.get('faults') and data['faults']:
                bmb_name = data['basic_info'].get('name', bmb_id)
                logger.warning(f"Bomba {bmb_name} tiene fallos reportados")
        
    except Exception as e:
        logger.error(f"Error en el proceso principal: {e}")


if __name__ == "__main__":
    main()