"""
Tests unitarios para el CLI principal de ADN.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from adn.cli import app


class TestAdnCli:
    """Tests para la aplicación CLI principal."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.runner = CliRunner()
    
    def test_version_command(self):
        """Test del comando version."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.stdout
    
    def test_version_verbose(self):
        """Test del comando version con flag verbose."""
        result = self.runner.invoke(app, ["version", "--verbose"])
        assert result.exit_code == 0
        assert "ADN CLI" in result.stdout
        assert "Python:" in result.stdout
    
    def test_help_command(self):
        """Test del comando help."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ADN CLI" in result.stdout
        assert "create" in result.stdout
        assert "config" in result.stdout
    
    @patch('adn.utils.file_handler.FileHandler.find_pdf_files')
    def test_list_files_empty_directory(self, mock_find_files):
        """Test listar archivos en directorio vacío."""
        mock_find_files.return_value = []
        
        result = self.runner.invoke(app, ["list-files"])
        assert result.exit_code == 0
        assert "No se encontraron" in result.stdout
    
    @patch('adn.utils.file_handler.FileHandler.find_pdf_files')
    @patch('adn.utils.file_handler.FileHandler.get_file_size')
    @patch('adn.utils.file_handler.FileHandler.is_processed')
    def test_list_files_with_pdfs(self, mock_is_processed, mock_get_size, mock_find_files):
        """Test listar archivos con PDFs existentes."""
        # Mock archivos PDF
        mock_pdf = MagicMock()
        mock_pdf.name = "test.pdf"
        mock_find_files.return_value = [mock_pdf]
        mock_get_size.return_value = "1.5 MB"
        mock_is_processed.return_value = False
        
        result = self.runner.invoke(app, ["list-files"])
        assert result.exit_code == 0
        assert "test.pdf" in result.stdout
    
    @patch('adn.utils.file_handler.FileHandler.find_pdf_files')
    def test_status_command(self, mock_find_files):
        """Test del comando status."""
        mock_find_files.return_value = []
        
        result = self.runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "Total de PDFs: 0" in result.stdout
    
    @patch('pathlib.Path.glob')
    def test_clean_command_no_temp_files(self, mock_glob):
        """Test comando clean sin archivos temporales."""
        mock_glob.return_value = []
        
        result = self.runner.invoke(app, ["clean"])
        assert result.exit_code == 0
        assert "No se encontraron archivos temporales" in result.stdout
    
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.unlink')
    def test_clean_command_with_temp_files(self, mock_unlink, mock_glob):
        """Test comando clean con archivos temporales."""
        # Mock archivo temporal
        mock_temp_file = MagicMock()
        mock_temp_file.name = "temp.tmp"
        mock_temp_file.unlink.return_value = None
        mock_glob.return_value = [mock_temp_file]
        
        result = self.runner.invoke(app, ["clean", "--force"])
        assert result.exit_code == 0
    
    def test_invalid_directory(self):
        """Test con directorio inválido."""
        result = self.runner.invoke(app, ["list-files", "/directorio/inexistente"])
        assert result.exit_code == 1
        assert "no existe" in result.stdout


class TestCreateCommand:
    """Tests para comandos de creación."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.runner = CliRunner()
    
    @patch('adn.utils.validators.validate_pdf_file')
    @patch('adn.utils.file_handler.FileHandler.generate_extraction_file')
    def test_create_file_success(self, mock_generate, mock_validate):
        """Test creación exitosa de archivo."""
        mock_validate.return_value = True
        mock_generate.return_value = Path("test_extraccion.md")
        
        result = self.runner.invoke(app, ["create", "file", "test.pdf"])
        assert result.exit_code == 0
        assert "Archivo creado" in result.stdout
    
    @patch('adn.utils.validators.validate_pdf_file')
    def test_create_file_invalid_pdf(self, mock_validate):
        """Test con archivo PDF inválido."""
        mock_validate.return_value = False
        
        result = self.runner.invoke(app, ["create", "file", "invalid.pdf"])
        assert result.exit_code == 1
        assert "no es un archivo PDF válido" in result.stdout
    
    @patch('adn.utils.file_handler.FileHandler.find_pdf_files')
    def test_create_all_no_files(self, mock_find_files):
        """Test create all sin archivos PDF."""
        mock_find_files.return_value = []
        
        result = self.runner.invoke(app, ["create", "all"])
        assert result.exit_code == 0
        assert "No se encontraron archivos PDF" in result.stdout


class TestConfigCommand:
    """Tests para comandos de configuración."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.runner = CliRunner()
    
    @patch('adn.utils.config.ConfigManager.init_config')
    def test_config_init_success(self, mock_init):
        """Test inicialización exitosa de configuración."""
        mock_init.return_value = Path("~/.adn/config.yaml")
        
        result = self.runner.invoke(app, ["config", "init"])
        assert result.exit_code == 0
        assert "Configuración inicializada" in result.stdout
    
    @patch('adn.utils.config.ConfigManager.init_config')
    def test_config_init_exists(self, mock_init):
        """Test inicialización con configuración existente."""
        mock_init.side_effect = FileExistsError()
        
        result = self.runner.invoke(app, ["config", "init"])
        assert result.exit_code == 1
        assert "ya existe" in result.stdout
    
    @patch('adn.utils.config.ConfigManager.get_config')
    def test_config_show(self, mock_get_config):
        """Test mostrar configuración."""
        mock_get_config.return_value = {
            "default_template": "default",
            "output_suffix": "_extraccion",
        }
        
        result = self.runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0
        assert "default_template" in result.stdout
    
    @patch('adn.utils.config.ConfigManager.get_config')
    def test_config_show_not_found(self, mock_get_config):
        """Test mostrar configuración no encontrada."""
        mock_get_config.side_effect = FileNotFoundError()
        
        result = self.runner.invoke(app, ["config", "show"])
        assert result.exit_code == 1
        assert "no encontrada" in result.stdout


@pytest.fixture
def temp_directory(tmp_path):
    """Fixture para directorio temporal."""
    return tmp_path


@pytest.fixture
def sample_pdf_file(temp_directory):
    """Fixture para archivo PDF de prueba."""
    pdf_file = temp_directory / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\nSample PDF content")
    return pdf_file