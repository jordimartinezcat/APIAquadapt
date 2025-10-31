# Formato de Fechas para AquaAdvanced API

## Formato Requerido por la API

La API de AquaAdvanced requiere que las fechas se envíen en un formato específico:

```
2025-10-22T00%3A00%3A00Z
```

### Características del Formato:

1. **Base ISO 8601**: `YYYY-MM-DDTHH:MM:SSZ`
2. **URL Encoding**: Los dos puntos (`:`) se codifican como `%3A`
3. **UTC Timezone**: Debe terminar con `Z` para indicar tiempo UTC
4. **Sin Fracciones**: Los microsegundos se eliminan

## Implementación

### Función de Conversión

La clase `AquaAdvancedClient` incluye el método `_format_datetime_for_api()` que convierte fechas ISO estándar al formato requerido:

```python
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
        if dt_string.endswith('Z'):
            dt_string = dt_string[:-1]

        # Parsear la fecha para validar formato
        dt = datetime.fromisoformat(dt_string)

        # Formatear como ISO con Z al final
        iso_with_z = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        # URL encode los dos puntos (:) que se convierten en %3A
        formatted = iso_with_z.replace(':', '%3A')

        logger.debug(f"Fecha convertida: {dt_string} -> {formatted}")
        return formatted

    except ValueError as e:
        logger.error(f"Error al formatear fecha {dt_string}: {e}")
        # Retornar el string original si no se puede procesar
        return dt_string
```

### Uso Automático

Todos los métodos del cliente que requieren fechas (`get_bomba_status`, `get_bomba_power`, `get_bomba_speed`) aplican automáticamente esta conversión:

```python
params = {}
if start_time:
    params["startTime"] = self._format_datetime_for_api(start_time)
if end_time:
    params["endTime"] = self._format_datetime_for_api(end_time)
```

## Ejemplos de Conversión

| Entrada                      | Salida API                 |
| ---------------------------- | -------------------------- |
| `2025-10-22T00:00:00`        | `2025-10-22T00%3A00%3A00Z` |
| `2025-10-22T14:30:45`        | `2025-10-22T14%3A30%3A45Z` |
| `2025-10-22T14:30:45.123456` | `2025-10-22T14%3A30%3A45Z` |
| `2025-10-22T00:00:00Z`       | `2025-10-22T00%3A00%3A00Z` |

## Testing

Puedes probar la conversión de fechas ejecutando:

```bash
python Tests/test_date_format.py
```

Este script muestra ejemplos de conversión y valida que el formato sea correcto.

## Compatibilidad

Esta implementación es compatible con:

- ✅ Fechas ISO 8601 estándar
- ✅ Fechas con microsegundos (se eliminan automáticamente)
- ✅ Fechas que ya incluyen 'Z' al final
- ✅ `datetime.isoformat()` de Python
- ✅ Fechas generadas por el main.py

## Notas Técnicas

1. **UTC Assumption**: Todas las fechas se tratan como UTC
2. **Error Handling**: Si una fecha no se puede parsear, se retorna sin cambios
3. **Logging**: Las conversiones se registran en nivel DEBUG
4. **Performance**: La conversión es muy eficiente, no afecta rendimiento

## Cambios Realizados

1. **Importación**: Agregado `from urllib.parse import quote`
2. **Método nuevo**: `_format_datetime_for_api()` en `AquaAdvancedClient`
3. **Actualización de métodos**: Modificados `get_bomba_status`, `get_bomba_power`, `get_bomba_speed`
4. **Test**: Creado `Tests/test_date_format.py` para validación

Todos los cambios son retrocompatibles - el código existente continúa funcionando sin modificaciones.
