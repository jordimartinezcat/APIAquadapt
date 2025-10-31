#!/usr/bin/env python3
"""
Script para arreglar archivos JSON con problemas de encoding (BOM UTF-8)
"""

import json
import os
import shutil
from datetime import datetime

def fix_json_bom(filename: str) -> bool:
    """
    Arregla un archivo JSON que tiene BOM UTF-8.
    
    Args:
        filename: Nombre del archivo a arreglar
        
    Returns:
        True si se arregló correctamente
    """
    if not os.path.exists(filename):
        print(f"❌ Archivo {filename} no encontrado")
        return False
    
    try:
        # Crear backup
        backup_name = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✅ Backup creado: {backup_name}")
        
        # Leer con utf-8-sig para manejar BOM
        with open(filename, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        # Escribir sin BOM (utf-8 normal)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Archivo {filename} arreglado correctamente")
        print(f"   - Elementos encontrados: {len(data) if isinstance(data, list) else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al arreglar {filename}: {e}")
        return False

def main():
    """Función principal."""
    print("🔧 Arreglando archivos JSON con problemas de BOM...")
    
    # Lista de archivos a revisar
    archivos_json = [
        "aquadapt BMB Id.json",
        "aquadapt_ids_names.csv"  # Por si acaso también tiene problemas
    ]
    
    for archivo in archivos_json:
        if os.path.exists(archivo):
            print(f"\n📁 Procesando {archivo}...")
            
            # Solo procesar si es JSON
            if archivo.endswith('.json'):
                fix_json_bom(archivo)
            else:
                print(f"   ⏭️ Saltando {archivo} (no es JSON)")
        else:
            print(f"\n📁 {archivo} no encontrado, saltando...")
    
    print("\n✨ Proceso completado")
    print("\n💡 Ahora puedes ejecutar tus scripts sin problemas de encoding")

if __name__ == '__main__':
    main()