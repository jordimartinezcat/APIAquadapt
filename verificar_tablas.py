#!/usr/bin/env python3
"""
Script para verificar y crear tablas necesarias en PostgreSQL
"""

import os
import sys

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "CAT_Conexions", "src")
)

from CAT_Conexions.src.conexions import pgDataLake


def verificar_tablas():
    """Verificar si las tablas existen"""
    db = pgDataLake()
    db.connect_database()

    print("🔍 Verificando tablas...\n")

    # Verificar schema ga_integration
    query_schemas = """
    SELECT schema_name 
    FROM information_schema.schemata 
    WHERE schema_name IN ('ga_integration', 'ga_landing');
    """
    df = db.get_data(query_schemas)
    print("📁 Schemas encontrados:")
    print(df)
    print()

    # Verificar tabla de mapeo
    query_mapeo = """
    SELECT table_name, table_schema 
    FROM information_schema.tables 
    WHERE table_schema = 'ga_integration' AND table_name = 'ite_aqapi_tag';
    """
    df = db.get_data(query_mapeo)
    print("📋 Tabla de mapeo (ga_integration.ite_aqapi_tag):")
    if len(df) > 0:
        print("✅ Existe")
        # Ver columnas
        query_cols = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'ga_integration' AND table_name = 'ite_aqapi_tag'
        ORDER BY ordinal_position;
        """
        df_cols = db.get_data(query_cols)
        print("\n  Columnas:")
        print(df_cols)
    else:
        print("❌ No existe")
    print()

    # Verificar tabla de datos
    query_hist = """
    SELECT table_name, table_schema 
    FROM information_schema.tables 
    WHERE table_schema = 'ga_landing' AND table_name = 'ite_aqapi_hist';
    """
    df = db.get_data(query_hist)
    print("📊 Tabla de datos (ga_landing.ite_aqapi_hist):")
    if len(df) > 0:
        print("✅ Existe")
        # Ver columnas
        query_cols = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'ga_landing' AND table_name = 'ite_aqapi_hist'
        ORDER BY ordinal_position;
        """
        df_cols = db.get_data(query_cols)
        print("\n  Columnas:")
        print(df_cols)
    else:
        print("❌ No existe")


def crear_tablas():
    """Crear tablas desde archivo SQL"""
    db = pgDataLake()
    db.connect_database()

    print("\n" + "=" * 70)
    print("🔨 CREANDO TABLAS")
    print("=" * 70 + "\n")

    # Leer archivo SQL
    with open("setup_database_tables.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Separar por comandos (esto es simplificado, para producción usa mejor parser)
    commands = [
        cmd.strip()
        for cmd in sql_content.split(";")
        if cmd.strip() and not cmd.strip().startswith("--")
    ]

    for i, cmd in enumerate(commands, 1):
        # Saltar comentarios en bloque
        if cmd.startswith("/*") or "/*" in cmd:
            continue

        try:
            print(f"\n📝 Ejecutando comando {i}/{len(commands)}...")
            result = db.get_data(cmd + ";")
            print(f"✅ OK")
        except Exception as e:
            print(f"⚠️ Error: {e}")
            # Continuar con el siguiente comando

    print("\n✅ Proceso completado")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Verificar o crear tablas en PostgreSQL"
    )
    parser.add_argument(
        "--crear",
        action="store_true",
        help="Crear tablas desde setup_database_tables.sql",
    )
    args = parser.parse_args()

    if args.crear:
        crear_tablas()
    else:
        verificar_tablas()
        verificar_tablas()
