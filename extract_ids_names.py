import json
import csv

# Leer el archivo JSON
with open(r'c:\temp\aquadapt BMB Id.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Extraer IDs y nombres
records = []
for item in data:
    records.append({
        'id': item.get('id', ''),
        'name': item.get('name', '')
    })

# Guardar en CSV
with open(r'c:\temp\aquadapt_ids_names.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'name'])
    writer.writeheader()
    writer.writerows(records)

print(f'Se han extraído {len(records)} registros y guardado en aquadapt_ids_names.csv')
print('Primeros 5 registros:')
for i, record in enumerate(records[:5]):
    print(f'{i+1}. ID: {record["id"]}, Name: {record["name"]}')