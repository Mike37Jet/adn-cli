"""
Funciones de validación para ADN CLI.
"""

import os
from pathlib import Path
from typing import List, Optional

from .logger import get_logger

logger = get_logger(__name__)


def validate_pdf_file(file_path: Path) -> bool:
    """
    Validar que un archivo es un PDF válido.
    
    Args:
        file_path: Ruta del archivo a validar
        
    Returns:
        bool: True si es un PDF válido
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    
    # Verificar que existe
    if not file_path.exists():
        logger.warning(f"Archivo no existe: {file_path}")
        return False
    
    # Verificar que es un archivo (no directorio)
    if not file_path.is_file():
        logger.warning(f"La ruta no es un archivo: {file_path}")
        return False
    
    # Verificar extensión
    if file_path.suffix.lower() != '.pdf':
        logger.warning(f"El archivo no tiene extensión .pdf: {file_path}")
        return False
    
    # Verificar header PDF básico
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                logger.warning(f"El archivo no tiene header PDF válido: {file_path}")
                return False
    except Exception as e:
        logger.error(f"Error leyendo archivo {file_path}: {e}")
        return False
    
    # Verificar que el archivo no está vacío
    if file_path.stat().st_size == 0:
        logger.warning(f"El archivo está vacío: {file_path}")
        return False
    
    return True


def validate_directory(directory: Path, create_if_missing: bool = False) -> bool:
    """
    Validar que un directorio existe y es accesible.
    
    Args:
        directory: Directorio a validar
        create_if_missing: Crear el directorio si no existe
        
    Returns:
        bool: True si el directorio es válido
    """
    if not isinstance(directory, Path):
        directory = Path(directory)
    
    # Si no existe y se permite crear
    if not directory.exists() and create_if_missing:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio creado: {directory}")
            return True
        except Exception as e:
            logger.error(f"Error creando directorio {directory}: {e}")
            return False
    
    # Verificar que existe
    if not directory.exists():
        logger.warning(f"Directorio no existe: {directory}")
        return False
    
    # Verificar que es un directorio
    if not directory.is_dir():
        logger.warning(f"La ruta no es un directorio: {directory}")
        return False
    
    # Verificar permisos de lectura
    if not os.access(directory, os.R_OK):
        logger.warning(f"Sin permisos de lectura en directorio: {directory}")
        return False
    
    return True


def validate_template_name(template_name: str) -> bool:
    """
    Validar que un nombre de template es válido.
    
    Args:
        template_name: Nombre del template a validar
        
    Returns:
        bool: True si el nombre es válido
    """
    if not template_name:
        logger.warning("Nombre de template vacío")
        return False
    
    # Verificar caracteres válidos
    invalid_chars = '<>:"/\\|?*'
    if any(char in template_name for char in invalid_chars):
        logger.warning(f"Nombre de template contiene caracteres inválidos: {template_name}")
        return False
    
    # Verificar longitud
    if len(template_name) > 50:
        logger.warning(f"Nombre de template muy largo: {template_name}")
        return False
    
    # Verificar que no empiece o termine con punto
    if template_name.startswith('.') or template_name.endswith('.'):
        logger.warning(f"Nombre de template no puede empezar o terminar con punto: {template_name}")
        return False
    
    return True


def validate_output_filename(filename: str, directory: Optional[Path] = None) -> bool:
    """
    Validar que un nombre de archivo de salida es válido.
    
    Args:
        filename: Nombre del archivo a validar
        directory: Directorio donde se creará el archivo (opcional)
        
    Returns:
        bool: True si el nombre es válido
    """
    if not filename:
        logger.warning("Nombre de archivo vacío")
        return False
    
    # Verificar caracteres válidos en el sistema de archivos
    invalid_chars = '<>:"/\\|?*'
    if any(char in filename for char in invalid_chars):
        logger.warning(f"Nombre de archivo contiene caracteres inválidos: {filename}")
        return False
    
    # Verificar longitud del nombre base (sin extensión)
    name_without_ext = Path(filename).stem
    if len(name_without_ext) > 100:
        logger.warning(f"Nombre de archivo muy largo: {filename}")
        return False
    
    # Verificar que tiene extensión .md
    if not filename.lower().endswith('.md'):
        logger.warning(f"Archivo de salida debe tener extensión .md: {filename}")
        return False
    
    # Si se proporciona directorio, verificar que se puede escribir
    if directory:
        if not validate_directory(directory):
            return False
        
        # Verificar permisos de escritura
        if not os.access(directory, os.W_OK):
            logger.warning(f"Sin permisos de escritura en directorio: {directory}")
            return False
    
    return True


def validate_config_value(key: str, value: any) -> bool:
    """
    Validar que un valor de configuración es válido.
    
    Args:
        key: Clave de configuración
        value: Valor a validar
        
    Returns:
        bool: True si el valor es válido
    """
    # Validaciones específicas por clave
    if key == "log_level":
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value not in valid_levels:
            logger.warning(f"Nivel de log inválido: {value}. Válidos: {valid_levels}")
            return False
    
    elif key == "default_template":
        if not validate_template_name(value):
            return False
    
    elif key == "output_suffix":
        if not isinstance(value, str):
            logger.warning(f"output_suffix debe ser string: {value}")
            return False
        if len(value) > 20:
            logger.warning(f"output_suffix muy largo: {value}")
            return False
    
    elif key == "default_output_dir":
        try:
            path = Path(value)
            if path.is_absolute() and not path.exists():
                logger.warning(f"Directorio de salida por defecto no existe: {value}")
                return False
        except Exception:
            logger.warning(f"Directorio de salida inválido: {value}")
            return False
    
    elif key == "auto_open_generated":
        if not isinstance(value, bool):
            logger.warning(f"auto_open_generated debe ser booleano: {value}")
            return False
    
    elif key == "encoding":
        try:
            "test".encode(value)
        except LookupError:
            logger.warning(f"Encoding inválido: {value}")
            return False
    
    elif key == "max_filename_length":
        if not isinstance(value, int) or value < 10 or value > 255:
            logger.warning(f"max_filename_length debe ser entero entre 10 y 255: {value}")
            return False
    
    return True


def validate_glob_pattern(pattern: str) -> bool:
    """
    Validar que un patrón glob es válido.
    
    Args:
        pattern: Patrón glob a validar
        
    Returns:
        bool: True si el patrón es válido
    """
    if not pattern:
        logger.warning("Patrón glob vacío")
        return False
    
    # Verificar que contiene caracteres válidos
    try:
        # Intentar usar el patrón en una ruta temporal
        Path("/tmp").glob(pattern)
        return True
    except Exception as e:
        logger.warning(f"Patrón glob inválido {pattern}: {e}")
        return False


def validate_file_permissions(file_path: Path, read: bool = False, write: bool = False) -> bool:
    """
    Validar permisos de archivo.
    
    Args:
        file_path: Archivo a verificar
        read: Verificar permisos de lectura
        write: Verificar permisos de escritura
        
    Returns:
        bool: True si tiene los permisos requeridos
    """
    if not file_path.exists():
        logger.warning(f"Archivo no existe: {file_path}")
        return False
    
    if read and not os.access(file_path, os.R_OK):
        logger.warning(f"Sin permisos de lectura: {file_path}")
        return False
    
    if write and not os.access(file_path, os.W_OK):
        logger.warning(f"Sin permisos de escritura: {file_path}")
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanear nombre de archivo removiendo caracteres problemáticos.
    
    Args:
        filename: Nombre de archivo original
        
    Returns:
        str: Nombre de archivo saneado
    """
    # Caracteres problemáticos
    invalid_chars = '<>:"/\\|?*'
    
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remover espacios múltiples
    sanitized = ' '.join(sanitized.split())
    
    # Reemplazar espacios por guiones bajos
    sanitized = sanitized.replace(' ', '_')
    
    # Remover puntos al inicio y final
    sanitized = sanitized.strip('.')
    
    # Limitar longitud
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:100 - len(ext)] + ext
    
    return sanitized


def get_validation_summary(
    pdf_files: List[Path],
    output_dir: Optional[Path] = None,
    template_name: Optional[str] = None
) -> dict:
    """
    Obtener resumen de validación para una operación.
    
    Args:
        pdf_files: Lista de archivos PDF a validar
        output_dir: Directorio de salida (opcional)
        template_name: Nombre del template (opcional)
        
    Returns:
        dict: Resumen de validación
    """
    summary = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "valid_files": [],
        "invalid_files": []
    }
    
    # Validar archivos PDF
    for pdf_file in pdf_files:
        if validate_pdf_file(pdf_file):
            summary["valid_files"].append(pdf_file)
        else:
            summary["invalid_files"].append(pdf_file)
            summary["errors"].append(f"Archivo PDF inválido: {pdf_file}")
    
    # Validar directorio de salida
    if output_dir and not validate_directory(output_dir, create_if_missing=True):
        summary["errors"].append(f"Directorio de salida inválido: {output_dir}")
    
    # Validar nombre de template
    if template_name and not validate_template_name(template_name):
        summary["errors"].append(f"Nombre de template inválido: {template_name}")
    
    # Marcar como inválido si hay errores
    if summary["errors"] or not summary["valid_files"]:
        summary["valid"] = False
    
    return summary