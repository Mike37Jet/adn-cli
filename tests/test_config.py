"""
Tests unitarios para el gestor de configuración.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from adn.utils.config import ConfigManager


class TestConfigManager:
    """Tests para el gestor de configuración."""
    
    def setup_method(self):
        """Configurar cada test."""
        # Usar directorio temporal para tests
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Patchear el directorio de configuración
        self.config_manager = ConfigManager()
        self.config_manager.config_dir = self.temp_dir
        self.config_manager.config_file = self.temp_dir / "config.yaml"
        self.config_manager.templates_dir = self.temp_dir / "templates"
        
        # Limpiar cache
        self.config_manager._config_cache = None
    
    def teardown_method(self):
        """Limpiar después de cada test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_config_new(self):
        """Test inicializar configuración nueva."""
        config_file = self.config_manager.init_config()
        
        assert config_file.exists()
        assert self.config_manager.templates_dir.exists()
        
        # Verificar contenido
        config = self.config_manager.get_config()
        assert "default_template" in config
        assert "output_suffix" in config
    
    def test_init_config_exists_without_force(self):
        """Test inicializar configuración existente sin force."""
        # Crear configuración existente
        self.config_manager.init_config()
        
        # Intentar crear de nuevo sin force
        with pytest.raises(FileExistsError):
            self.config_manager.init_config(force=False)
    
    def test_init_config_exists_with_force(self):
        """Test inicializar configuración existente con force."""
        # Crear configuración existente
        self.config_manager.init_config()
        
        # Crear de nuevo con force
        config_file = self.config_manager.init_config(force=True)
        assert config_file.exists()
    
    def test_get_config_not_exists(self):
        """Test obtener configuración que no existe."""
        with pytest.raises(FileNotFoundError):
            self.config_manager.get_config()
    
    def test_get_config_valid(self):
        """Test obtener configuración válida."""
        self.config_manager.init_config()
        config = self.config_manager.get_config()
        
        assert isinstance(config, dict)
        assert "default_template" in config
        assert config["default_template"] == "default"
    
    def test_set_config(self):
        """Test establecer valor de configuración."""
        self.config_manager.init_config()
        
        self.config_manager.set_config("default_template", "custom")
        
        config = self.config_manager.get_config()
        assert config["default_template"] == "custom"
    
    def test_get_config_value_exists(self):
        """Test obtener valor específico existente."""
        self.config_manager.init_config()
        
        value = self.config_manager.get_config_value("default_template")
        assert value == "default"
    
    def test_get_config_value_not_exists(self):
        """Test obtener valor específico no existente."""
        self.config_manager.init_config()
        
        value = self.config_manager.get_config_value("no_existe", "valor_default")
        assert value == "valor_default"
    
    def test_get_config_value_no_file(self):
        """Test obtener valor sin archivo de configuración."""
        value = self.config_manager.get_config_value("default_template")
        assert value == "default"  # Valor por defecto
    
    def test_reset_config(self):
        """Test restablecer configuración."""
        self.config_manager.init_config()
        self.config_manager.set_config("default_template", "custom")
        
        self.config_manager.reset_config()
        
        config = self.config_manager.get_config()
        assert config["default_template"] == "default"
    
    def test_validate_config_valid(self):
        """Test validar configuración válida."""
        self.config_manager.init_config()
        
        result = self.config_manager.validate_config()
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_config_invalid_log_level(self):
        """Test validar configuración con log_level inválido."""
        self.config_manager.init_config()
        self.config_manager.set_config("log_level", "INVALID")
        
        result = self.config_manager.validate_config()
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_config_invalid_encoding(self):
        """Test validar configuración con encoding inválido."""
        self.config_manager.init_config()
        self.config_manager.set_config("encoding", "invalid-encoding")
        
        result = self.config_manager.validate_config()
        assert result["valid"] is False
        assert any("Encoding inválido" in error for error in result["errors"])
    
    def test_backup_config(self):
        """Test crear respaldo de configuración."""
        self.config_manager.init_config()
        
        backup_file = self.config_manager.backup_config()
        
        assert backup_file.exists()
        assert backup_file.name.startswith("config_backup_")
        assert backup_file.suffix == ".yaml"
    
    def test_backup_config_no_file(self):
        """Test crear respaldo sin archivo de configuración."""
        with pytest.raises(FileNotFoundError):
            self.config_manager.backup_config()
    
    def test_restore_config(self):
        """Test restaurar configuración desde respaldo."""
        # Crear configuración inicial
        self.config_manager.init_config()
        self.config_manager.set_config("default_template", "original")
        
        # Crear respaldo
        backup_file = self.config_manager.backup_config()
        
        # Modificar configuración
        self.config_manager.set_config("default_template", "modificado")
        
        # Restaurar desde respaldo
        self.config_manager.restore_config(backup_file)
        
        # Verificar restauración
        config = self.config_manager.get_config()
        assert config["default_template"] == "original"
    
    def test_restore_config_invalid_file(self):
        """Test restaurar configuración desde archivo inválido."""
        invalid_file = self.temp_dir / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: content: [")
        
        with pytest.raises(ValueError):
            self.config_manager.restore_config(invalid_file)
    
    def test_restore_config_not_exists(self):
        """Test restaurar configuración desde archivo inexistente."""
        non_existent = self.temp_dir / "no_existe.yaml"
        
        with pytest.raises(FileNotFoundError):
            self.config_manager.restore_config(non_existent)
    
    def test_config_caching(self):
        """Test que la configuración se cachea correctamente."""
        self.config_manager.init_config()
        
        # Primera lectura
        config1 = self.config_manager.get_config()
        
        # Segunda lectura (desde cache)
        config2 = self.config_manager.get_config()
        
        assert config1 == config2
        assert self.config_manager._config_cache is not None
    
    def test_cache_invalidation_on_set(self):
        """Test que el cache se invalida al establecer valores."""
        self.config_manager.init_config()
        
        # Cargar configuración en cache
        self.config_manager.get_config()
        assert self.config_manager._config_cache is not None
        
        # Modificar configuración
        self.config_manager.set_config("test_key", "test_value")
        
        # Cache debería haberse invalidado
        assert self.config_manager._config_cache is None
    
    @patch("yaml.safe_load")
    def test_handle_yaml_error(self, mock_yaml_load):
        """Test manejo de errores YAML."""
        self.config_manager.init_config()
        
        # Simular error YAML
        import yaml
        mock_yaml_load.side_effect = yaml.YAMLError("Error de prueba")
        
        with pytest.raises(yaml.YAMLError):
            self.config_manager.get_config()


@pytest.fixture
def config_manager():
    """Fixture para ConfigManager con directorio temporal."""
    temp_dir = Path(tempfile.mkdtemp())
    
    manager = ConfigManager()
    manager.config_dir = temp_dir
    manager.config_file = temp_dir / "config.yaml"
    manager.templates_dir = temp_dir / "templates"
    manager._config_cache = None
    
    yield manager
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)