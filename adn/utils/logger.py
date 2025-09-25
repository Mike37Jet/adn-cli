"""
Sistema de logging para ADN CLI.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler

# Logger principal del proyecto
_logger_initialized = False


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> None:
    """
    Configurar el sistema de logging para ADN CLI.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo de log (opcional)
        console_output: Mostrar logs en consola
    """
    global _logger_initialized
    
    if _logger_initialized:
        return
    
    # Configurar nivel de logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Obtener logger principal
    logger = logging.getLogger("adn")
    logger.setLevel(numeric_level)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Formato para logs
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para consola con Rich
    if console_output:
        console_handler = RichHandler(
            console=None,  # Usa la consola por defecto
            show_time=False,  # Rich muestra su propio tiempo
            show_path=False,
            markup=True,
        )
        console_handler.setLevel(numeric_level)
        logger.addHandler(console_handler)
    
    # Handler para archivo
    if log_file:
        # Asegurar que el directorio existe
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Archivo siempre recibe todo
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configurar loggers de librerías externas
    _configure_external_loggers()
    
    _logger_initialized = True
    logger.debug("Sistema de logging inicializado")


def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Asegurar que el logging está inicializado
    if not _logger_initialized:
        setup_logging()
    
    # Crear logger hijo del logger principal
    if not name.startswith("adn"):
        name = f"adn.{name}"
    
    return logging.getLogger(name)


def _configure_external_loggers() -> None:
    """Configurar niveles de logging para librerías externas."""
    
    # Reducir verbosidad de librerías externas
    external_loggers = [
        "urllib3",
        "requests",
        "jinja2",
        "yaml",
        "rich",
    ]
    
    for logger_name in external_loggers:
        ext_logger = logging.getLogger(logger_name)
        ext_logger.setLevel(logging.WARNING)


class LoggingContext:
    """Context manager para logging temporal con configuración específica."""
    
    def __init__(self, level: str = "INFO", logger_name: str = "adn"):
        """
        Inicializar contexto de logging.
        
        Args:
            level: Nivel de logging temporal
            logger_name: Nombre del logger a modificar
        """
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.new_level = getattr(logging, level.upper(), logging.INFO)
    
    def __enter__(self):
        """Entrar al contexto."""
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salir del contexto."""
        self.logger.setLevel(self.original_level)


def configure_logging_from_config():
    """Configurar logging basado en la configuración del usuario."""
    try:
        from .config import ConfigManager
        
        config_manager = ConfigManager()
        
        # Obtener configuración
        log_level = config_manager.get_config_value("log_level", "INFO")
        
        # Configurar archivo de log
        logs_dir = config_manager.config_dir / "logs"
        log_file = logs_dir / "adn.log"
        
        # Configurar logging
        setup_logging(
            level=log_level,
            log_file=log_file,
            console_output=True
        )
        
    except Exception:
        # Si hay error con la configuración, usar configuración por defecto
        setup_logging(level="INFO", console_output=True)


# Configurar logging automáticamente cuando se importa el módulo
configure_logging_from_config()