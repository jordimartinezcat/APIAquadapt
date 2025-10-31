#!/usr/bin/env python3
"""
AquaAdvanced API Client - Versión Oficial Corregida
Cliente para la API de AquaAdvanced basado en la documentación oficial
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
import urllib3

import config

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Deshabilitar warnings de SSL si está configurado
if hasattr(config, "DISABLE_SSL_WARNINGS") and config.DISABLE_SSL_WARNINGS:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AquaAdvancedClient:
    """Cliente oficial para la API de AquaAdvanced"""

    def __init__(self):
        """Inicializar cliente con configuración"""
        self.config = config
        self.base_url = config.API_BASE_URL
        self.headers = self._get_headers()
        self.timeout = getattr(config, "REQUEST_TIMEOUT", 10)
        self.retry_count = getattr(config, "RETRY_COUNT", 3)
        self.verify_ssl = getattr(config, "VERIFY_SSL", False)

        logger.info("Usando autenticación por API Key")

    def _format_datetime_for_api(self, dt_string: str) -> str:
        """
        Convertir fecha ISO a formato requerido por la API

        Args:
            dt_string: Fecha en formato ISO (ej: '2025-10-22T00:00:00')

        Returns:
            Fecha en formato API URL-encoded (ej: '2025-10-22T00%3A00%3A00Z')
        """
        try:
            # Si la fecha ya tiene Z al final, la removemos temporalmente
            if dt_string.endswith("Z"):
                dt_string = dt_string[:-1]

            # Parsear la fecha para validar formato
            dt = datetime.fromisoformat(dt_string)

            # Formatear como ISO con Z al final
            iso_with_z = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            # URL encode los dos puntos (:) que se convierten en %3A
            # formatted = iso_with_z.replace(":", "%3A")
            formatted = iso_with_z

            logger.debug(f"Fecha convertida: {dt_string} -> {formatted}")
            return formatted

        except ValueError as e:
            logger.error(f"Error al formatear fecha {dt_string}: {e}")
            # Retornar el string original si no se puede procesar
            return dt_string

    def _get_headers(self) -> Dict[str, str]:
        """Obtener headers para las peticiones"""
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if hasattr(config, "API_KEY") and config.API_KEY:
            headers["X-Api-Key"] = config.API_KEY

        return headers

    def _handle_api_response(self, response: requests.Response) -> Any:
        """Manejar respuesta de la API con BOM UTF-8 y respuestas vacías"""
        # Detectar y manejar BOM UTF-8 en la respuesta
        content = response.content
        if content.startswith(b"\xef\xbb\xbf"):
            content = content[3:]  # Eliminar BOM

        # Manejar respuestas vacías
        if not content.strip():
            logger.info(
                "Respuesta vacía. Puede que no haya datos para el rango especificado."
            )
            return []

        try:
            # Intentar decodificar como JSON
            return json.loads(content.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.warning(f"Error al decodificar JSON: {e}")
            logger.debug(f"Contenido de respuesta: {content[:200]}...")
            return []

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> requests.Response:
        """
        Realizar petición HTTP con reintentos

        Args:
            method: Método HTTP
            endpoint: Endpoint de la API
            params: Parámetros de la petición

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
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                )

                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                if response.status_code in [401, 403]:
                    logger.error(f"Error de autenticación: {e}")
                    raise
                elif response.status_code == 404:
                    logger.error(f"Endpoint no encontrado: {url}")
                    raise
                elif response.status_code >= 500:
                    logger.error(f"Error del servidor ({response.status_code})")
                    if attempt < self.retry_count - 1:
                        logger.warning(
                            f"Intento {attempt + 1}/{self.retry_count} falló: {e}"
                        )
                        continue
                    raise
                else:
                    raise
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    logger.warning(
                        f"Intento {attempt + 1}/{self.retry_count} falló: {e}"
                    )
                    continue
                raise

        raise requests.exceptions.RequestException(
            f"Falló después de {self.retry_count} intentos"
        )

    def get_bombas_list(self) -> List[Dict]:
        """
        Obtener lista de bombas desde la API o archivo local

        Returns:
            Lista de bombas con sus IDs y nombres
        """
        try:
            # Intentar obtener desde la API
            response = self._make_request("GET", config.ENDPOINTS["pumps_list"])
            content = response.content

            # Detectar y manejar BOM UTF-8
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]

            data = json.loads(content.decode("utf-8"))

            # Manejar diferentes formatos de respuesta
            if isinstance(data, dict) and "results" in data:
                pumps = data["results"]
            elif isinstance(data, list):
                pumps = data
            else:
                logger.warning(f"Formato de respuesta inesperado: {type(data)}")
                pumps = []

            logger.info(f"Obtenidas {len(pumps)} bombas de la API")
            return pumps

        except Exception as e:
            logger.error(f"Error al obtener bombas de la API: {e}")
            logger.info("Intentando cargar desde archivo local...")
            return load_bmb_list_from_file()

    def get_bomba_info(self, bomba_id: str) -> Dict:
        """
        Obtener información detallada de una bomba

        Args:
            bomba_id: ID de la bomba

        Returns:
            Información de la bomba con enlaces href
        """
        try:
            endpoint = f"{config.ENDPOINTS['individual_pump']}/{bomba_id}/"
            response = self._make_request("GET", endpoint)

            content = response.content
            if content.startswith(b"\xef\xbb\xbf"):
                content = content[3:]

            return json.loads(content.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error al obtener info de bomba {bomba_id}: {e}")
            return {}

    def get_bomba_status(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Any:
        """
        Obtener estado de una bomba usando los enlaces href

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

            params = {}
            if start_time:
                params["startTime"] = self._format_datetime_for_api(start_time)
            if end_time:
                params["endTime"] = self._format_datetime_for_api(end_time)

            # Hacer petición directa con el href
            response = requests.get(
                href,
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return self._handle_api_response(response)
        except Exception as e:
            logger.error(f"Error al obtener status de bomba {bomba_id}: {e}")
            logger.debug(
                f"URL utilizada: {href if 'href' in locals() else 'No disponible'}"
            )
            return []

    def get_bomba_power(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Any:
        """
        Obtener potencia de una bomba usando los enlaces href

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

            params = {}
            if start_time:
                params["startTime"] = self._format_datetime_for_api(start_time)
            if end_time:
                params["endTime"] = self._format_datetime_for_api(end_time)

            # Hacer petición directa con el href
            response = requests.get(
                href,
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return self._handle_api_response(response)
        except Exception as e:
            logger.error(f"Error al obtener potencia de bomba {bomba_id}: {e}")
            logger.debug(
                f"URL utilizada: {href if 'href' in locals() else 'No disponible'}"
            )
            return []

    def get_bomba_speed(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Any:
        """
        Obtener velocidad de una bomba usando los enlaces href

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

            params = {}
            if start_time:
                params["startTime"] = self._format_datetime_for_api(start_time)
            if end_time:
                params["endTime"] = self._format_datetime_for_api(end_time)

            # Hacer petición directa con el href
            response = requests.get(
                href,
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return self._handle_api_response(response)
        except Exception as e:
            logger.error(f"Error al obtener velocidad de bomba {bomba_id}: {e}")
            logger.debug(
                f"URL utilizada: {href if 'href' in locals() else 'No disponible'}"
            )
            return []

    def get_bomba_onoffschedule(
        self,
        bomba_id: str,
        start_time: str = None,
        end_time: str = None,
        detailed: bool = False,
    ) -> Any:
        """
        Obtener programación de encendido/apagado de una bomba usando los enlaces href

        Args:
            bomba_id: ID de la bomba
            start_time: Tiempo inicio en formato ISO8601
            end_time: Tiempo fin en formato ISO8601
            detailed: Si usar endpoint detallado

        Returns:
            Datos de programación de encendido/apagado de la bomba
        """
        try:
            # Primero obtener info de la bomba para los enlaces href
            info = self.get_bomba_info(bomba_id)
            if not info:
                return {}

            # Usar el href proporcionado por la API
            endpoint_key = "onoffschedule/detailed" if detailed else "onoffschedule"
            if endpoint_key not in info:
                logger.error(
                    f"Endpoint {endpoint_key} no disponible para bomba {bomba_id}"
                )
                return {}

            href = info[endpoint_key]["href"].replace(
                "https://aquadvanced.ccaait.local",
                "https://aquadvanced.ccaait.local/publication/physicalPumps/"
                + f"{bomba_id}",
            )

            params = {}
            if start_time:
                params["startTime"] = self._format_datetime_for_api(start_time)
            if end_time:
                params["endTime"] = self._format_datetime_for_api(end_time)

            # Hacer petición directa con el href
            response = requests.get(
                href,
                params=params,
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
            response.raise_for_status()

            return self._handle_api_response(response)
        except Exception as e:
            logger.error(f"Error al obtener velocidad de bomba {bomba_id}: {e}")
            logger.debug(
                f"URL utilizada: {href if 'href' in locals() else 'No disponible'}"
            )
            return []


def load_bmb_list_from_file(file_path: str = "aquadapt BMB Id.json") -> List[Dict]:
    """
    Cargar lista de bombas desde archivo JSON local

    Args:
        file_path: Ruta al archivo JSON

    Returns:
        Lista de bombas con sus IDs y nombres
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"Archivo no encontrado: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        if isinstance(data, dict) and "results" in data:
            pumps = data["results"]
        elif isinstance(data, list):
            pumps = data
        else:
            logger.error("Formato de archivo no válido")
            return []

        logger.info(f"Cargadas {len(pumps)} bombas desde archivo local")
        return pumps

    except Exception as e:
        logger.error(f"Error al cargar archivo {file_path}: {e}")
        return []


if __name__ == "__main__":
    # Ejemplo de uso básico
    client = AquaAdvancedClient()
    bombas = client.get_bombas_list()

    if bombas:
        print(f"Encontradas {len(bombas)} bombas")
        for bmb in bombas[:3]:  # Mostrar primeras 3
            print(f"- {bmb.get('name', 'Sin nombre')} (ID: {bmb['id']})")
    else:
        print("No se pudieron obtener las bombas")
