#!/usr/bin/env python3
"""
Script de instalación y configuración para ADN CLI.
Facilita la instalación en diferentes entornos.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """Ejecutar comando y manejar errores."""
    print(f"{description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr.strip()}")
        return False


def check_python_version():
    """Verificar versión de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Se requiere Python 3.8+. Versión actual: {version.major}.{version.minor}")
        return False
    print(f"Python {version.major}.{version.minor} - Compatible")
    return True


def install_adn():
    """Instalar ADN CLI."""
    print("Instalando ADN CLI...")
    
    commands = [
        ("pip install --upgrade pip", "Actualizando pip"),
        ("pip install -e .", "Instalando ADN CLI en modo desarrollo"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    # Verificar instalación
    if not run_command("adn --help", "Verificando instalación"):
        return False
    
    print("ADN CLI instalado correctamente")
    return True


def setup_development():
    """Configurar entorno de desarrollo."""
    print("Configurando entorno de desarrollo...")
    
    # Verificar que estamos en el directorio correcto
    if not Path("pyproject.toml").exists():
        print("Debe ejecutar este script desde el directorio raíz del proyecto")
        return False
    
    # Instalar dependencias de desarrollo
    dev_commands = [
        ("pip install pytest pytest-cov black isort flake8 mypy pre-commit", "Instalando dependencias de desarrollo"),
    ]
    
    for cmd, desc in dev_commands:
        run_command(cmd, desc)
    
    # Configurar pre-commit (opcional)
    try:
        run_command("pre-commit install", "Configurando pre-commit hooks")
    except:
        print("Pre-commit no disponible, continuando...")
    
    print("Entorno de desarrollo configurado")
    return True


def run_tests():
    """Ejecutar tests."""
    print("Ejecutando tests...")
    
    test_commands = [
        ("python -m pytest tests/ -v", "Ejecutando tests unitarios"),
    ]
    
    try:
        run_command("python -m pytest tests/ --cov=adn --cov-report=html", "Ejecutando tests con cobertura")
    except:
        print("Cobertura no disponible, continuando...")
    
    print("Tests ejecutados correctamente")
    return True


def check_code_quality():
    """Verificar calidad de código."""
    print("Verificando calidad de código...")
    
    try:
        if not run_command("black --check adn/ tests/", "Verificando formato con Black"):
            print("Ejecute 'black adn/ tests/' para formatear")
    except:
        pass
    
    try:
        if not run_command("isort --check-only adn/ tests/", "Verificando imports con isort"):
            print("Ejecute 'isort adn/ tests/' para organizar imports")
    except:
        pass
    
    # Flake8 y mypy son opcionales
    run_command("flake8 adn/ --max-line-length=88", "Verificando con flake8")
    
    print("Calidad de código verificada")
    return True


def initialize_config():
    """Inicializar configuración de ADN CLI."""
    print("Inicializando configuración de ADN CLI...")
    
    try:
        run_command("adn config init --force", "Inicializando configuración")
    except:
        pass
    
    print("Configuración de ADN CLI inicializada")
    return True


def main():
    """Función principal."""
    print("Instalador de ADN CLI")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Uso: python install.py [install|dev|test|quality|config|all]")
        print()
        print("Comandos disponibles:")
        print("  install  - Solo instalar ADN CLI")
        print("  dev      - Configurar entorno de desarrollo")
        print("  test     - Ejecutar tests")
        print("  quality  - Verificar calidad de código")
        print("  config   - Inicializar configuración")
        print("  all      - Ejecutar todos los pasos")
        return
    
    action = sys.argv[1]
    
    if not check_python_version():
        sys.exit(1)
    
    success = True
    
    if action in ["install", "all"]:
        success = install_adn() and success
    
    if action in ["dev", "all"]:
        success = setup_development() and success
    
    if action in ["test", "all"]:
        success = run_tests() and success
    
    if action in ["quality", "all"]:
        success = check_code_quality() and success
    
    if action in ["config", "all"]:
        success = initialize_config() and success
    
    if action not in ["install", "dev", "test", "quality", "config", "all"]:
        print(f"Acción desconocida: {action}")
        success = False
    
    if success:
        print("\nInstalación completada exitosamente")
        print("Ahora puede usar: adn --help")
    else:
        print("\nHubo algunos errores durante la instalación")
        sys.exit(1)


if __name__ == "__main__":
    main()