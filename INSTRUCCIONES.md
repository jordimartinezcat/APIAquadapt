# Instrucciones de Instalación y Uso

## 📦 Dependencias Requeridas

```bash
pip install requests urllib3
```

## 🔧 Configuración Inicial

1. **Verificar API Key en config.py**:

   ```python
   API_KEY = "EAK__27af3e6b5c94474d8948cf19659df3f2"
   ```

2. **Verificar URL base**:
   ```python
   API_BASE_URL = "https://aquadvanced.ccaait.local/publication"
   ```

## 🚀 Ejecución

### Demostración Completa

```bash
python demostracion_final.py
```

### Test Rápido

```bash
python test_simple.py
```

### Uso en tu propio código

```python
from aquadapt_api_client_oficial_v2 import AquaAdvancedClient

client = AquaAdvancedClient()
bombas = client.get_bombas_list()
```

## 📋 Verificación de Funcionamiento

Deberías ver:

- ✅ 73 bombas encontradas
- ✅ Información detallada obtenible
- ✅ 16 endpoints disponibles por bomba
- ⚠️ Warnings de JSON son normales (respuestas vacías)

## 🆘 Solución de Problemas

- **Error de conexión**: Verificar VPN/red interna
- **Error de autenticación**: Verificar API Key
- **Respuestas vacías**: Normal, no hay datos en el rango consultado
