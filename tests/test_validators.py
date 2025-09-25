"""
Tests unitarios para validadores.
"""

import pytest
from pathlib import Path
import tempfile

from adn.utils.validators import (
    validate_pdf_file,
    validate_directory,
    validate_template_name,
    validate_output_filename,
    validate_config_value,
    sanitize_filename,
    get_validation_summary
)


class TestValidators:
    """Tests para funciones de validación."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Limpiar después de cada test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_pdf_file_valid(self):
        """Test validar PDF válido."""
        pdf_file = self.temp_dir / "valid.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContenido del PDF")
        
        assert validate_pdf_file(pdf_file) is True
    
    def test_validate_pdf_file_invalid_extension(self):
        """Test validar archivo sin extensión PDF."""
        txt_file = self.temp_dir / "not_pdf.txt"
        txt_file.write_text("No es un PDF")
        
        assert validate_pdf_file(txt_file) is False
    
    def test_validate_pdf_file_invalid_header(self):
        """Test validar PDF con header inválido."""
        fake_pdf = self.temp_dir / "fake.pdf"
        fake_pdf.write_text("No tiene header PDF")
        
        assert validate_pdf_file(fake_pdf) is False
    
    def test_validate_pdf_file_nonexistent(self):
        """Test validar PDF inexistente."""
        nonexistent = self.temp_dir / "no_existe.pdf"
        
        assert validate_pdf_file(nonexistent) is False
    
    def test_validate_pdf_file_empty(self):
        """Test validar PDF vacío."""
        empty_pdf = self.temp_dir / "empty.pdf"
        empty_pdf.write_bytes(b"")
        
        assert validate_pdf_file(empty_pdf) is False
    
    def test_validate_directory_exists(self):
        """Test validar directorio existente."""
        existing_dir = self.temp_dir / "existing"
        existing_dir.mkdir()
        
        assert validate_directory(existing_dir) is True
    
    def test_validate_directory_nonexistent_no_create(self):
        """Test validar directorio inexistente sin crear."""
        nonexistent = self.temp_dir / "no_existe"
        
        assert validate_directory(nonexistent, create_if_missing=False) is False
    
    def test_validate_directory_nonexistent_with_create(self):
        """Test validar directorio inexistente con creación."""
        nonexistent = self.temp_dir / "no_existe"
        
        assert validate_directory(nonexistent, create_if_missing=True) is True
        assert nonexistent.exists()
    
    def test_validate_directory_file_instead_of_dir(self):
        """Test validar archivo en lugar de directorio."""
        file_path = self.temp_dir / "archivo.txt"
        file_path.write_text("contenido")
        
        assert validate_directory(file_path) is False
    
    def test_validate_template_name_valid(self):
        """Test validar nombre de template válido."""
        assert validate_template_name("mi-template") is True
        assert validate_template_name("template123") is True
        assert validate_template_name("academic_paper") is True
    
    def test_validate_template_name_invalid_chars(self):
        """Test validar nombre con caracteres inválidos."""
        assert validate_template_name("template<>") is False
        assert validate_template_name("template/path") is False
        assert validate_template_name("template:name") is False
    
    def test_validate_template_name_empty(self):
        """Test validar nombre de template vacío."""
        assert validate_template_name("") is False
        assert validate_template_name(None) is False
    
    def test_validate_template_name_too_long(self):
        """Test validar nombre muy largo."""
        long_name = "a" * 60
        assert validate_template_name(long_name) is False
    
    def test_validate_template_name_with_dots(self):
        """Test validar nombre que empieza/termina con punto."""
        assert validate_template_name(".template") is False
        assert validate_template_name("template.") is False
        assert validate_template_name("tem.plate") is True  # Punto en el medio es válido
    
    def test_validate_output_filename_valid(self):
        """Test validar nombre de archivo de salida válido."""
        assert validate_output_filename("documento.md") is True
        assert validate_output_filename("archivo_extraccion.md") is True
    
    def test_validate_output_filename_invalid_extension(self):
        """Test validar archivo sin extensión .md."""
        assert validate_output_filename("documento.txt") is False
        assert validate_output_filename("documento.pdf") is False
        assert validate_output_filename("documento") is False
    
    def test_validate_output_filename_invalid_chars(self):
        """Test validar nombre con caracteres inválidos."""
        assert validate_output_filename("archivo<>.md") is False
        assert validate_output_filename("archivo/path.md") is False
    
    def test_validate_output_filename_too_long(self):
        """Test validar nombre muy largo."""
        long_name = "a" * 150 + ".md"
        assert validate_output_filename(long_name) is False
    
    def test_validate_config_value_log_level(self):
        """Test validar valores de log_level."""
        assert validate_config_value("log_level", "DEBUG") is True
        assert validate_config_value("log_level", "INFO") is True
        assert validate_config_value("log_level", "INVALID") is False
    
    def test_validate_config_value_template(self):
        """Test validar nombre de template en configuración."""
        assert validate_config_value("default_template", "valid-name") is True
        assert validate_config_value("default_template", "invalid<>name") is False
    
    def test_validate_config_value_output_suffix(self):
        """Test validar sufijo de salida."""
        assert validate_config_value("output_suffix", "_extraccion") is True
        assert validate_config_value("output_suffix", "a" * 25) is False
        assert validate_config_value("output_suffix", 123) is False
    
    def test_validate_config_value_auto_open(self):
        """Test validar valor booleano."""
        assert validate_config_value("auto_open_generated", True) is True
        assert validate_config_value("auto_open_generated", False) is True
        assert validate_config_value("auto_open_generated", "true") is False
    
    def test_validate_config_value_encoding(self):
        """Test validar encoding."""
        assert validate_config_value("encoding", "utf-8") is True
        assert validate_config_value("encoding", "latin-1") is True
        assert validate_config_value("encoding", "invalid-encoding") is False
    
    def test_validate_config_value_max_filename_length(self):
        """Test validar longitud máxima de nombres."""
        assert validate_config_value("max_filename_length", 100) is True
        assert validate_config_value("max_filename_length", 5) is False  # Muy corto
        assert validate_config_value("max_filename_length", 300) is False  # Muy largo
        assert validate_config_value("max_filename_length", "100") is False  # No es int
    
    def test_sanitize_filename_basic(self):
        """Test sanear nombre de archivo básico."""
        result = sanitize_filename("archivo con espacios.pdf")
        assert " " not in result
        assert "_" in result
    
    def test_sanitize_filename_invalid_chars(self):
        """Test sanear caracteres inválidos."""
        dirty = "archivo<>:\"/\\|?*.pdf"
        clean = sanitize_filename(dirty)
        
        invalid_chars = '<>:"/\\|?*'
        assert not any(char in clean for char in invalid_chars)
    
    def test_sanitize_filename_multiple_spaces(self):
        """Test sanear espacios múltiples."""
        result = sanitize_filename("archivo    con    espacios.pdf")
        assert "    " not in result
        assert result.count("_") == 2  # Solo dos guiones bajos
    
    def test_sanitize_filename_dots(self):
        """Test sanear puntos al inicio/final."""
        assert not sanitize_filename(".archivo.pdf").startswith(".")
        assert not sanitize_filename("archivo.pdf.").endswith(".")
    
    def test_sanitize_filename_too_long(self):
        """Test sanear nombre muy largo."""
        long_name = "a" * 150 + ".pdf"
        result = sanitize_filename(long_name)
        
        assert len(result) <= 100
        assert result.endswith(".pdf")
    
    def test_get_validation_summary_all_valid(self):
        """Test resumen de validación con todos los archivos válidos."""
        # Crear PDFs válidos
        pdf1 = self.temp_dir / "doc1.pdf"
        pdf2 = self.temp_dir / "doc2.pdf"
        pdf1.write_bytes(b"%PDF-1.4\nContent1")
        pdf2.write_bytes(b"%PDF-1.4\nContent2")
        
        summary = get_validation_summary([pdf1, pdf2])
        
        assert summary["valid"] is True
        assert len(summary["valid_files"]) == 2
        assert len(summary["invalid_files"]) == 0
        assert len(summary["errors"]) == 0
    
    def test_get_validation_summary_some_invalid(self):
        """Test resumen de validación con algunos archivos inválidos."""
        # Crear un PDF válido y uno inválido
        valid_pdf = self.temp_dir / "valid.pdf"
        invalid_pdf = self.temp_dir / "invalid.pdf"
        
        valid_pdf.write_bytes(b"%PDF-1.4\nContent")
        invalid_pdf.write_text("No es PDF")
        
        summary = get_validation_summary([valid_pdf, invalid_pdf])
        
        assert summary["valid"] is False
        assert len(summary["valid_files"]) == 1
        assert len(summary["invalid_files"]) == 1
        assert len(summary["errors"]) >= 1
    
    def test_get_validation_summary_no_files(self):
        """Test resumen de validación sin archivos."""
        summary = get_validation_summary([])
        
        assert summary["valid"] is False
        assert len(summary["valid_files"]) == 0
        assert len(summary["invalid_files"]) == 0
    
    def test_get_validation_summary_with_template(self):
        """Test resumen incluyendo validación de template."""
        pdf_file = self.temp_dir / "doc.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        # Template válido
        summary = get_validation_summary([pdf_file], template_name="valid-template")
        assert summary["valid"] is True
        
        # Template inválido
        summary = get_validation_summary([pdf_file], template_name="invalid<>template")
        assert summary["valid"] is False