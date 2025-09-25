"""
Gestor de configuración para ADN CLI.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

from .logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Gestor de configuración para ADN CLI."""
    
    def __init__(self):
        """Inicializar el gestor de configuración."""
        # Determinar directorio de configuración
        if os.name == 'nt':  # Windows
            base_dir = Path.home() / "AppData" / "Roaming" / "adn-cli"
        else:  # Unix/Linux/macOS
            base_dir = Path.home() / ".adn"
        
        self.config_dir = base_dir
        self.config_file = self.config_dir / "config.yaml"
        
        # Usar templates del proyecto por defecto, fallback a directorio de usuario
        project_templates = Path(__file__).parent.parent / "templates"
        user_templates = self.config_dir / "templates"
        
        # Priorizar templates del proyecto si existe, sino usar directorio de usuario
        if project_templates.exists():
            self.templates_dir = project_templates
        else:
            self.templates_dir = user_templates
        
        # Configuración por defecto
        self._default_config = {
            "default_template": "default",
            "output_suffix": "_extraccion",
            "default_output_dir": ".",
            "log_level": "INFO",
            "auto_open_generated": False,
            "preserve_structure": True,
            "date_format": "%d/%m/%Y %H:%M",
            "encoding": "utf-8",
            "max_filename_length": 100,
        }
        
        # Cache de configuración
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def init_config(self, force: bool = False) -> Path:
        """
        Inicializar configuración con valores por defecto.
        
        Args:
            force: Sobrescribir configuración existente
            
        Returns:
            Path: Ruta del archivo de configuración creado
            
        Raises:
            FileExistsError: Si la configuración ya existe y force=False
        """
        if self.config_file.exists() and not force:
            raise FileExistsError("La configuración ya existe")
        
        # Crear directorios necesarios
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear directorio de logs
        logs_dir = self.config_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Escribir configuración por defecto
        self._write_config(self._default_config)
        
        # Invalidar cache
        self._config_cache = None
        
        logger.info(f"Configuración inicializada en {self.config_file}")
        return self.config_file
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtener la configuración actual.
        
        Returns:
            Dict: Configuración actual
            
        Raises:
            FileNotFoundError: Si no existe el archivo de configuración
        """
        # Usar cache si está disponible
        if self._config_cache is not None:
            return self._config_cache.copy()
        
        if not self.config_file.exists():
            raise FileNotFoundError("Archivo de configuración no encontrado")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # Combinar con configuración por defecto
            full_config = self._default_config.copy()
            full_config.update(config)
            
            # Actualizar cache
            self._config_cache = full_config.copy()
            
            return full_config
            
        except yaml.YAMLError as e:
            logger.error(f"Error leyendo configuración YAML: {e}")
            raise
        except Exception as e:
            logger.error(f"Error leyendo configuración: {e}")
            raise
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Establecer un valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        # Obtener configuración actual
        try:
            config = self.get_config()
        except FileNotFoundError:
            # Si no existe, crear con valores por defecto
            config = self._default_config.copy()
        
        # Actualizar valor
        config[key] = value
        
        # Escribir configuración
        self._write_config(config)
        
        # Invalidar cache
        self._config_cache = None
        
        logger.info(f"Configuración actualizada: {key} = {value}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Obtener un valor específico de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Any: Valor de configuración
        """
        try:
            config = self.get_config()
            return config.get(key, default)
        except FileNotFoundError:
            return self._default_config.get(key, default)
    
    def reset_config(self) -> None:
        """Restablecer configuración a valores por defecto."""
        self._write_config(self._default_config)
        self._config_cache = None
        logger.info("Configuración restablecida a valores por defecto")
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validar la configuración actual.
        
        Returns:
            Dict: Resultado de validación con errores si los hay
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            config = self.get_config()
            
            # Validar log_level
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if config.get("log_level") not in valid_log_levels:
                result["errors"].append(
                    f"log_level inválido: {config.get('log_level')}. "
                    f"Valores válidos: {', '.join(valid_log_levels)}"
                )
            
            # Validar default_output_dir
            output_dir = Path(config.get("default_output_dir", "."))
            if not output_dir.exists():
                result["warnings"].append(
                    f"Directorio de salida no existe: {output_dir}"
                )
            
            # Validar template por defecto
            default_template = config.get("default_template", "default")
            template_file = self.templates_dir / f"{default_template}.md"
            if not template_file.exists():
                result["warnings"].append(
                    f"Template por defecto no encontrado: {default_template}"
                )
            
            # Validar encoding
            try:
                "test".encode(config.get("encoding", "utf-8"))
            except LookupError:
                result["errors"].append(
                    f"Encoding inválido: {config.get('encoding')}"
                )
            
            if result["errors"]:
                result["valid"] = False
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error validando configuración: {e}")
        
        return result
    
    def _write_config(self, config: Dict[str, Any]) -> None:
        """
        Escribir configuración al archivo.
        
        Args:
            config: Configuración a escribir
        """
        # Asegurar que el directorio existe
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    config, 
                    f, 
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                    sort_keys=True
                )
                
        except Exception as e:
            logger.error(f"Error escribiendo configuración: {e}")
            raise
    
    def backup_config(self) -> Path:
        """
        Crear respaldo de la configuración actual.
        
        Returns:
            Path: Ruta del archivo de respaldo
        """
        import datetime
        
        if not self.config_file.exists():
            raise FileNotFoundError("No hay configuración para respaldar")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.config_dir / f"config_backup_{timestamp}.yaml"
        
        backup_file.write_bytes(self.config_file.read_bytes())
        
        logger.info(f"Respaldo creado: {backup_file}")
        return backup_file
    
    def restore_config(self, backup_file: Path) -> None:
        """
        Restaurar configuración desde un respaldo.
        
        Args:
            backup_file: Archivo de respaldo
        """
        if not backup_file.exists():
            raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_file}")
        
        # Validar que es un archivo YAML válido
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Archivo de respaldo no válido: {e}")
        
        # Hacer respaldo de la configuración actual antes de restaurar
        if self.config_file.exists():
            self.backup_config()
        
        # Restaurar configuración
        self.config_file.write_bytes(backup_file.read_bytes())
        
        # Invalidar cache
        self._config_cache = None
        
        logger.info(f"Configuración restaurada desde: {backup_file}")


# Instancia global del gestor de configuración
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Obtener instancia global del gestor de configuración."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager