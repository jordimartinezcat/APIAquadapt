#!/usr/bin/env python3
"""
Script de instalación y configuración para el proyecto APIAquadapt
Ejecuta este script para configurar el entorno y verificar dependencias
"""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def install_dependencies():
    """Instalar dependencias necesarias"""
    dependencies = ["requests", "urllib3"]

    print("\n📦 Verificando dependencias...")

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"⚠️ Instalando {dep}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ {dep} - Instalado")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando {dep}")
                return False

    return True


def verify_files():
    """Verificar que todos los archivos necesarios estén presentes"""
    required_files = [
        "aquadapt_api_client_oficial_v2.py",
        "config.py",
        "ejemplos_uso_corregido.py",
        "aquadapt BMB Id.json",
    ]

    print("\n📁 Verificando archivos del proyecto...")

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - Falta")
            return False

    return True


def test_api_client():
    """Probar el cliente de API"""
    print("\n🧪 Probando cliente de API...")

    try:
        # Import the client
        from aquadapt_api_client_oficial_v2 import AquaAdvancedClient

        # Create client instance
        client = AquaAdvancedClient()
        print("✅ Cliente creado correctamente")

        # Test loading pumps list
        bombas = client.get_bombas_list()
        if bombas:
            print(f"✅ Lista de bombas cargada: {len(bombas)} bombas")
        else:
            print("⚠️ No se pudieron cargar las bombas (normal si no hay conexión)")

        return True

    except Exception as e:
        print(f"❌ Error probando cliente: {e}")
        return False


def main():
    """Función principal de configuración"""
    print("=" * 60)
    print("🚀 CONFIGURACIÓN DEL PROYECTO APIAquadapt")
    print("=" * 60)

    # Verificar Python
    if not check_python_version():
        return False

    # Instalar dependencias
    if not install_dependencies():
        return False

    # Verificar archivos
    if not verify_files():
        return False

    # Probar cliente
    if not test_api_client():
        return False

    print("\n" + "=" * 60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("✅ Proyecto listo para usar")
    print("\n🚀 Comandos disponibles:")
    print("   python ejemplos_uso_corregido.py    - Ejemplos interactivos")
    print("   python demostracion_final.py        - Demostración completa")
    print("\n📖 Lee README.md para más información")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
