# Configuración para el cliente de API AquaAdvanced

# URL base de la API (según documentación oficial)
API_BASE_URL = "https://aquadvanced.ccaait.local/publication"

# Configuración de autenticación
# Opción 1: API Key (recomendado según documentación)
API_KEY = (
    "EAK__27af3e6b5c94474d8948cf19659df3f2"  # Ej: "Em2sApiKey" - Header: X-Api-Key
)

# Opción 2: OAuth2 (más avanzado)
OAUTH2_CLIENT_ID = None
OAUTH2_CLIENT_SECRET = None
OAUTH2_SCOPE = "aquadvanced-energy.api.scope"

# Opción 3: Usuario y contraseña (si aplica)
USERNAME = None  # Ej: "admin"
PASSWORD = None  # Ej: "password123"

# Configuración de conexión
VERIFY_SSL = False  # Cambiar a True si usas certificados válidos
DISABLE_SSL_WARNINGS = (
    True  # Deshabilitar warnings de SSL para certificados autofirmados
)
TIMEOUT = 30  # Timeout en segundos
RETRY_COUNT = 3  # Número de reintentos en caso de error

# Configuración de logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = None  # Ej: "aquadapt_api.log" para guardar logs en archivo

# Archivos
BMB_JSON_FILE = "aquadapt BMB Id.json"  # Archivo con lista de bombas
OUTPUT_DIR = "."  # Directorio para guardar resultados

# Endpoints oficiales según documentación de la API
ENDPOINTS = {
    # Bombas físicas (Physical Pumps)
    "pumps_list": "/physicalPumps/",  # Lista todas las bombas
    "individual_pump": "/physicalPumps",  # Base para información específica de bomba
    "status": "/physicalPumps/{bmb_id}/status/",
    "detailed_status": "/physicalPumps/{bmb_id}/status/detailed/",
    "power": "/physicalPumps/{bmb_id}/rawpower/",
    "detailed_power": "/physicalPumps/{bmb_id}/rawpower/detailed/",
    "speed": "/physicalPumps/{bmb_id}/speed/",
    "detailed_speed": "/physicalPumps/{bmb_id}/speed/detailed/",
    "faults": "/physicalPumps/{bmb_id}/fault/",
    "detailed_faults": "/physicalPumps/{bmb_id}/fault/detailed/",
    "control": "/physicalPumps/{bmb_id}/aaecontrol/",
    "detailed_control": "/physicalPumps/{bmb_id}/aaecontrol/detailed/",
    "inservice": "/physicalPumps/{bmb_id}/inservice/",
    "detailed_inservice": "/physicalPumps/{bmb_id}/inservice/detailed/",
    "onoff_schedule": "/physicalPumps/{bmb_id}/onoffschedule/",
    "flow_schedule": "/physicalPumps/{bmb_id}/flowschedule/",
    # Otros equipos disponibles
    "flowmeters": "/physicalflowmeters/",
    "pressure_meters": "/physicalpressuremeters/",
    "tanks": "/physicaltanks/",
    "valves": "/valves/",
    "pump_stations": "/pumpStations/",
    "sources": "/physicalSources/",
}

# Configuración de datos a obtener
DATA_TO_COLLECT = ["status", "detailed_status", "power", "speed", "faults"]

# Filtros
FILTER_BY_NAME = None  # Ej: ["EB0", "EB3"] para filtrar solo ciertas bombas
EXCLUDE_OFFLINE = True  # Excluir bombas fuera de servicio

# Configuración de formato de salida
OUTPUT_FORMAT = "json"  # json, csv, excel
INCLUDE_TIMESTAMP = True
SEPARATE_FILES = False  # True para crear un archivo por bomba
