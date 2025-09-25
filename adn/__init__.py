"""
ADN CLI - Automatización de Documentos y Notas

Un framework CLI profesional para automatizar la creación de documentos de extracción 
y notas estructuradas a partir de archivos PDF.
"""

__version__ = "1.0.0"
__author__ = "ADN CLI Team"
__email__ = "contact@adn-cli.com"
__description__ = "Framework CLI para automatización de documentos y notas"

# Importaciones principales
from .cli import app
from .utils.config import ConfigManager
from .utils.logger import get_logger

__all__ = ["app", "ConfigManager", "get_logger"]