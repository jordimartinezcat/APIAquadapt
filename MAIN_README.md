# 🚀 Main.py - Consulta Simple API AquaAdvanced

Script interactivo para realizar consultas personalizadas a la API de AquaAdvanced.

## ✨ Características

- 🎯 **Interfaz Simple**: Menús interactivos paso a paso
- 📅 **Fechas Flexibles**: Soporte para fechas relativas y absolutas
- 🔍 **12 Endpoints**: Todos los endpoints de bomba disponibles
- 🔥 **Consultas Múltiples**: Opción para consultar varios endpoints a la vez
- 💾 **Guardado Automático**: Opción para guardar resultados en JSON
- 📊 **Visualización Clara**: Resumen detallado de resultados

## 🚀 Uso

```bash
python main.py
```

## 📋 Opciones de Fechas

### Fechas Relativas (Recomendado)

- `hoy` o `today` → Últimas 24 horas
- `ayer` o `yesterday` → Ayer completo
- `semana` o `week` → Última semana

### Fechas Absolutas

- `2025-10-23` → Fecha específica
- `2025-10-23 14:30` → Fecha y hora específica

## 📡 Endpoints Disponibles

### Básicos

1. **status** - Estado actual
2. **power** - Potencia (rawpower)
3. **speed** - Velocidad

### Detallados

4. **detailed_status** - Estado detallado
5. **detailed_power** - Potencia detallada
6. **detailed_speed** - Velocidad detallada

### Otros

7. **faults** - Fallos/Errores
8. **control** - Control AAE
9. **inservice** - En servicio

### Consultas Múltiples 🔥

13. **all_basic** - Status, Power, Speed (3 consultas)
14. **all_detailed** - Versiones detalladas (3 consultas)

## 💾 Guardado de Resultados

Los archivos se guardan con formato:

```
consulta_{endpoint}_{bomba}_{timestamp}.json
```

Ejemplo: `consulta_status_EB3_G4_20251024_093052.json`

## 📊 Formato de Resultados

```json
{
  "bomba": {
    "id": "040b3d5d-a68a-dc52-0623-5d2f6fcd2682",
    "name": "EB3 G4"
  },
  "endpoint": "status",
  "rango": {
    "inicio": "2025-10-23T09:30:14",
    "fin": "2025-10-24T23:59:00"
  },
  "datos": [...],
  "timestamp_consulta": "2025-10-24T09:30:52"
}
```

## 🎯 Casos de Uso

### Consulta Rápida de Estado

1. Ejecutar `python main.py`
2. Seleccionar bomba
3. Elegir "status"
4. Usar "hoy" para fechas
5. Ver resultados

### Análisis Detallado Semanal

1. Ejecutar `python main.py`
2. Seleccionar bomba crítica
3. Elegir "all_detailed"
4. Usar "semana" para rango
5. Guardar resultados para análisis

### Consulta de Potencia Específica

1. Ejecutar `python main.py`
2. Seleccionar bomba
3. Elegir "detailed_power"
4. Especificar fechas exactas
5. Analizar datos de consumo

## ⚠️ Notas Importantes

- **Respuestas vacías son normales** cuando no hay datos en el rango
- **Certificados SSL deshabilitados** para red interna
- **API Key configurada** en config.py
- **73 bombas disponibles** en el sistema

## 🔧 Dependencias

- `requests` - Cliente HTTP
- `json` - Manejo de JSON
- `datetime` - Manejo de fechas

## 🆘 Solución de Problemas

**Error de conexión**: Verificar red/VPN interna
**Sin datos**: Normal, probar otro rango de fechas
**Error de autenticación**: Verificar API_KEY en config.py

---

**✅ Listo para usar - Interfaz simple y poderosa**
