#!/usr/bin/env python3
"""
AquaAdvanced API Client - Versión Oficial
Cliente para la API de AquaAdvanced basado en la documentación oficial
"""

import requests
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib3
import conf            # La URL ya está completa, usar directamente
            response = requests.get(href, params=params, headers=self.headers, 
                                  verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            
            return self._handle_api_response(response)
        except Exception as e:
            logger.error(f"Error al obtener status de bomba {bomba_id}: {e}")
            return {}urar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AquaAdvancedClient:
    """Cliente oficial para la API de AquaAdvanced"""

    def __init__(self):
        """Inicializa el cliente usando la configuración oficial."""
        self.base_url = config.API_BASE_URL
        self.verify_ssl = config.VERIFY_SSL
        self.timeout = config.TIMEOUT
        self.retry_count = config.RETRY_COUNT

        # Configurar headers base
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AquaAdvanced-Python-Client/1.0",
        }

        # Configurar autenticación según documentación oficial
        self.auth = None
        if config.API_KEY:
            # Método preferido: API Key según documentación
            self.headers["X-Api-Key"] = config.API_KEY
            self.auth_method = "apikey"
            logger.info("Usando autenticación por API Key")
        elif config.USERNAME and config.PASSWORD:
            # Método alternativo: Basic Auth
            self.auth = (config.USERNAME, config.PASSWORD)
            self.auth_method = "basic"
            logger.info("Usando autenticación básica")
        elif hasattr(config, "OAUTH2_CLIENT_ID") and config.OAUTH2_CLIENT_ID:
            # OAuth2 (requiere implementación adicional)
            self.auth_method = "oauth2"
            logger.warning("OAuth2 configurado pero no implementado en esta versión")
        else:
            self.auth_method = "none"
            logger.warning("Sin autenticación configurada")

        # Configurar logging
        self._setup_logging()

        # Suprimir warnings de SSL si está deshabilitado
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _setup_logging(self):
        """Configura el sistema de logging."""
        if config.LOG_FILE:
            file_handler = logging.FileHandler(config.LOG_FILE)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(file_handler)

    def _make_request(
        self, endpoint: str, params: Dict = None, method: str = "GET"
    ) -> requests.Response:
        """
        Realiza una petición HTTP a la API.

        Args:
            endpoint: Endpoint de la API
            params: Parámetros de la petición
            method: Método HTTP

        Returns:
            Respuesta de la API

        Raises:
            requests.RequestException: Error en la petición
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retry_count):
            try:
                logger.debug(f"Realizando petición {method} a {url}")

                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    auth=self.auth,
                    params=params,
                    verify=self.verify_ssl,
                    timeout=self.timeout,
                )

                logger.debug(f"Respuesta: {response.status_code}")

                if response.status_code == 401:
                    logger.error(
                        "Error de autenticación (401). Verifica las credenciales."
                    )
                elif response.status_code == 403:
                    logger.error("Acceso denegado (403). Verifica permisos.")
                elif response.status_code == 404:
                    logger.error("Recurso no encontrado (404).")
                elif response.status_code >= 500:
                    logger.error(f"Error del servidor ({response.status_code})")

                response.raise_for_status()

                # Verificar si la respuesta tiene BOM UTF-8 y corregirlo
                if response.content.startswith(b"\xef\xbb\xbf"):
                    # Crear nueva respuesta sin BOM
                    import io

                    content_without_bom = response.content[
                        3:
                    ]  # Remover los 3 bytes del BOM
                    response._content = content_without_bom

                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1}/{self.retry_count} falló: {e}")
                if attempt == self.retry_count - 1:
                    raise

        raise requests.RequestException("Todos los reintentos fallaron")

    def get_bombas_list(self) -> List[Dict]:
        """
        Obtiene la lista de todas las bombas físicas.
        Intenta primero desde la API, luego desde archivo local si falla.

        Returns:
            Lista de bombas con su información básica
        """
        try:
            response = self._make_request(config.ENDPOINTS["bmb_list"])
            bombas = response.json()
            logger.info(f"Obtenidas {len(bombas)} bombas de la API")
            return bombas
        except Exception as e:
            logger.warning(f"Error al obtener lista de bombas de la API: {e}")

            # Intentar cargar desde archivo local como fallback
            logger.info("Intentando cargar desde archivo local...")
            bombas_local = load_bmb_list_from_file(config.BMB_JSON_FILE)

            if bombas_local:
                logger.info(f"Cargadas {len(bombas_local)} bombas desde archivo local")
                return bombas_local
            else:
                logger.error(
                    "No se pudieron obtener bombas ni de API ni de archivo local"
                )
                return []

    def _handle_api_response(self, response: requests.Response) -> Any:
        """Manejar respuesta de la API con BOM UTF-8 y respuestas vacías"""
        # Detectar y manejar BOM UTF-8 en la respuesta
        content = response.content
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]  # Eliminar BOM
        
        # Manejar respuestas vacías
        if not content.strip():
            logger.info("Respuesta vacía. Puede que no haya datos para el rango especificado.")
            return []
            
        return json.loads(content.decode('utf-8'))
    
    def get_bomba_info(self, bomba_id: str) -> Dict:
        """
        Obtiene información detallada de una bomba específica.

        Args:
            bomba_id: ID de la bomba

        Returns:
            Información de la bomba
        """
        try:
            endpoint = config.ENDPOINTS["bmb_info"].format(bmb_id=bomba_id)
            response = self._make_request(endpoint)
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener info de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_status(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene el estado de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Estado de la bomba
        """
        try:
            # Primero obtener info de la bomba para los enlaces href
            info = self.get_bomba_info(bomba_id)
            if not info:
                return {}

            # Usar el href proporcionado por la API
            endpoint_key = "status/detailed" if detailed else "status"
            if endpoint_key not in info:
                logger.error(
                    f"Endpoint {endpoint_key} no disponible para bomba {bomba_id}"
                )
                return {}

            href = info[endpoint_key]["href"]
            # Convertir href relativo a absoluto si es necesario
            if not href.startswith("http"):
                href = f"{self.config.API_BASE_URL.rstrip('/')}/{href.lstrip('/')}"

            params = {}
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time

            # La URL ya está completa, usar directamente
            response = requests.get(
                href,
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            # Detectar y manejar BOM UTF-8 en la respuesta
            content = response.content
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]  # Eliminar BOM

            return json.loads(content.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error al obtener status de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_power(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene la potencia de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Datos de potencia de la bomba
        """
        try:
            # Primero obtener info de la bomba para los enlaces href
            info = self.get_bomba_info(bomba_id)
            if not info:
                return {}

            # Usar el href proporcionado por la API
            endpoint_key = "rawpower/detailed" if detailed else "rawpower"
            if endpoint_key not in info:
                logger.error(
                    f"Endpoint {endpoint_key} no disponible para bomba {bomba_id}"
                )
                return {}

            href = info[endpoint_key]["href"]
            # Convertir href relativo a absoluto si es necesario
            if not href.startswith("http"):
                href = f"{self.config.API_BASE_URL.rstrip('/')}/{href.lstrip('/')}"

            params = {}
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time

            # La URL ya está completa, usar directamente
            response = requests.get(href, params=params, headers=self.headers, 
                                  verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            
            # Detectar y manejar BOM UTF-8 en la respuesta
            content = response.content
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]  # Eliminar BOM
                
            return json.loads(content.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error al obtener potencia de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_speed(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene la velocidad de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Datos de velocidad de la bomba
        """
        try:
            # Primero obtener info de la bomba para los enlaces href
            info = self.get_bomba_info(bomba_id)
            if not info:
                return {}

            # Usar el href proporcionado por la API
            endpoint_key = "speed/detailed" if detailed else "speed"
            if endpoint_key not in info:
                logger.error(
                    f"Endpoint {endpoint_key} no disponible para bomba {bomba_id}"
                )
                return {}

            href = info[endpoint_key]["href"]
            # Convertir href relativo a absoluto si es necesario
            if not href.startswith("http"):
                href = f"{self.config.API_BASE_URL.rstrip('/')}/{href.lstrip('/')}"

            params = {}
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time

            # La URL ya está completa, usar directamente
            response = requests.get(href, params=params, headers=self.headers, 
                                  verify=self.verify_ssl, timeout=self.timeout)
            response.raise_for_status()
            
            # Detectar y manejar BOM UTF-8 en la respuesta
            content = response.content
            if content.startswith(b'\xef\xbb\xbf'):
                content = content[3:]  # Eliminar BOM
                
            return json.loads(content.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error al obtener velocidad de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_faults(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene los fallos de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Datos de fallos de la bomba
        """
        try:
            endpoint_key = "detailed_faults" if detailed else "faults"
            endpoint = config.ENDPOINTS[endpoint_key].format(bmb_id=bomba_id)

            params = {}
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time

            response = self._make_request(endpoint, params)
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener fallos de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_inservice(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene el estado de servicio de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Datos de estado de servicio
        """
        try:
            endpoint_key = "detailed_inservice" if detailed else "inservice"
            endpoint = config.ENDPOINTS[endpoint_key].format(bmb_id=bomba_id)

            params = {}
            if start_time:
                params["startTime"] = start_time
            if end_time:
                params["endTime"] = end_time

            response = self._make_request(endpoint, params)
            return response.json()
        except Exception as e:
            logger.error(f"Error al obtener estado servicio bomba {bomba_id}: {e}")
            return {}

    def get_all_bomba_data(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Dict:
        """
        Obtiene todos los datos disponibles de una bomba.

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoints detallados

        Returns:
            Diccionario con todos los datos de la bomba
        """
        logger.info(f"Obteniendo datos completos de bomba {bomba_id}")

        data = {
            "bomba_id": bomba_id,
            "timestamp": datetime.now().isoformat(),
            "info": self.get_bomba_info(bomba_id),
            "status": self.get_bomba_status(bomba_id, start_time, end_time, detailed),
            "power": self.get_bomba_power(bomba_id, start_time, end_time, detailed),
            "speed": self.get_bomba_speed(bomba_id, start_time, end_time, detailed),
            "faults": self.get_bomba_faults(bomba_id, start_time, end_time, detailed),
            "inservice": self.get_bomba_inservice(
                bomba_id, start_time, end_time, detailed
            ),
        }

        return data

    def test_connection(self) -> bool:
        """
        Prueba la conexión con la API.

        Returns:
            True si la conexión es exitosa
        """
        try:
            logger.info("Probando conexión con la API...")
            response = self._make_request(config.ENDPOINTS["bmb_list"])
            logger.info("✓ Conexión exitosa con la API")
            return True
        except Exception as e:
            logger.error(f"✗ Error de conexión: {e}")
            return False


def load_bmb_list_from_file(filename: str) -> List[Dict]:
    """
    Carga la lista de bombas desde un archivo JSON local.
    Maneja archivos con BOM UTF-8 correctamente.

    Args:
        filename: Nombre del archivo JSON

    Returns:
        Lista de bombas desde el archivo
    """
    if not os.path.exists(filename):
        logger.warning(f"Archivo {filename} no encontrado")
        return []

    try:
        # Intentar primero con encoding utf-8-sig para manejar BOM
        with open(filename, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        logger.info(f"Archivo {filename} cargado correctamente con {len(data)} bombas")
        return data

    except UnicodeDecodeError:
        # Si falla, intentar con utf-8 normal
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(
                f"Archivo {filename} cargado correctamente con {len(data)} bombas"
            )
            return data
        except Exception as e:
            logger.error(f"Error al cargar archivo {filename}: {e}")
            return []

    except json.JSONDecodeError as e:
        logger.error(f"Error de formato JSON en {filename}: {e}")
        return []

    except Exception as e:
        logger.error(f"Error al cargar archivo {filename}: {e}")
        return []


def main():
    """Función principal para pruebas."""
    # Crear cliente
    client = AquaAdvancedClient()

    # Probar conexión
    if not client.test_connection():
        print("No se pudo conectar a la API. Verifica la configuración.")

        # Si no hay conexión, intentar cargar desde archivo local
        print("Intentando cargar datos desde archivo local...")
        bmb_list = load_bmb_list_from_file(config.BMB_JSON_FILE)

        if bmb_list:
            print(f"✅ Archivo local cargado: {len(bmb_list)} bombas encontradas")
            # Mostrar algunas bombas de ejemplo
            for i, bomba in enumerate(bmb_list[:3]):
                print(
                    f"Bomba {i+1}: {bomba.get('name', 'Sin nombre')} - ID: {bomba.get('id', 'Sin ID')}"
                )
        else:
            print("❌ No se pudo cargar archivo local tampoco")
        return

    print("¡Conexión exitosa! Cliente listo para usar.")

    # Ejemplo de uso básico
    try:
        # Obtener lista de bombas
        bombas = client.get_bombas_list()
        print(f"Encontradas {len(bombas)} bombas")

        if bombas:
            # Mostrar primera bomba como ejemplo
            primera_bomba = bombas[0]
            bomba_id = primera_bomba.get("id", "")
            print(f"Bomba ejemplo: {primera_bomba}")

            if bomba_id:
                # Obtener datos de la primera bomba
                info = client.get_bomba_info(bomba_id)
                print(f"Info bomba {bomba_id}: {info}")

    except Exception as e:
        logger.error(f"Error en ejemplo: {e}")


if __name__ == "__main__":
    main()
