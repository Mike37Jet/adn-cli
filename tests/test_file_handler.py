"""
Tests unitarios para el manejador de archivos.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from adn.utils.file_handler import FileHandler


class TestFileHandler:
    """Tests para el manejador de archivos."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_handler = FileHandler()
        
        # Patchear configuración para usar directorio temporal
        with patch.object(self.file_handler.config_manager, 'config_dir', self.temp_dir):
            pass
    
    def teardown_method(self):
        """Limpiar después de cada test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_find_pdf_files_empty_directory(self):
        """Test buscar PDFs en directorio vacío."""
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        pdf_files = self.file_handler.find_pdf_files(empty_dir)
        assert len(pdf_files) == 0
    
    def test_find_pdf_files_with_pdfs(self):
        """Test buscar PDFs en directorio con archivos."""
        # Crear archivos de prueba
        (self.temp_dir / "document1.pdf").write_bytes(b"%PDF-1.4\nContent")
        (self.temp_dir / "document2.pdf").write_bytes(b"%PDF-1.4\nContent")
        (self.temp_dir / "document3.txt").write_text("Not a PDF")
        
        pdf_files = self.file_handler.find_pdf_files(self.temp_dir)
        
        assert len(pdf_files) == 2
        assert all(f.suffix.lower() == '.pdf' for f in pdf_files)
    
    def test_find_pdf_files_with_pattern(self):
        """Test buscar PDFs con patrón específico."""
        # Crear archivos de prueba
        (self.temp_dir / "report_2023.pdf").write_bytes(b"%PDF-1.4\nContent")
        (self.temp_dir / "report_2024.pdf").write_bytes(b"%PDF-1.4\nContent")
        (self.temp_dir / "other.pdf").write_bytes(b"%PDF-1.4\nContent")
        
        pdf_files = self.file_handler.find_pdf_files(self.temp_dir, "report_*.pdf")
        
        assert len(pdf_files) == 2
        assert all("report_" in f.name for f in pdf_files)
    
    def test_find_pdf_files_nonexistent_directory(self):
        """Test buscar PDFs en directorio inexistente."""
        non_existent = self.temp_dir / "no_existe"
        
        with pytest.raises(FileNotFoundError):
            self.file_handler.find_pdf_files(non_existent)
    
    def test_find_pdf_files_not_directory(self):
        """Test buscar PDFs en archivo en lugar de directorio."""
        file_path = self.temp_dir / "archivo.txt"
        file_path.write_text("content")
        
        with pytest.raises(ValueError):
            self.file_handler.find_pdf_files(file_path)
    
    @patch('adn.utils.template_engine.TemplateEngine.render_template')
    def test_generate_extraction_file_success(self, mock_render):
        """Test generar archivo de extracción exitosamente."""
        # Crear PDF de prueba
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        # Mock template rendering
        mock_render.return_value = "# Contenido del template"
        
        output_file = self.file_handler.generate_extraction_file(pdf_file)
        
        assert output_file.exists()
        assert output_file.suffix == '.md'
        assert "extraccion" in output_file.name
    
    def test_generate_extraction_file_nonexistent_pdf(self):
        """Test generar archivo para PDF inexistente."""
        non_existent_pdf = self.temp_dir / "no_existe.pdf"
        
        with pytest.raises(FileNotFoundError):
            self.file_handler.generate_extraction_file(non_existent_pdf)
    
    @patch('adn.utils.template_engine.TemplateEngine.render_template')
    def test_generate_extraction_file_exists_no_force(self, mock_render):
        """Test generar archivo cuando ya existe sin force."""
        # Crear PDF y archivo de extracción existente
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        existing_file = self.temp_dir / "test_extraccion.md"
        existing_file.write_text("Contenido existente")
        
        mock_render.return_value = "# Nuevo contenido"
        
        with pytest.raises(FileExistsError):
            self.file_handler.generate_extraction_file(pdf_file, force=False)
    
    @patch('adn.utils.template_engine.TemplateEngine.render_template')
    def test_generate_extraction_file_exists_with_force(self, mock_render):
        """Test generar archivo cuando ya existe con force."""
        # Crear PDF y archivo de extracción existente
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        existing_file = self.temp_dir / "test_extraccion.md"
        existing_file.write_text("Contenido existente")
        
        mock_render.return_value = "# Nuevo contenido"
        
        output_file = self.file_handler.generate_extraction_file(pdf_file, force=True)
        
        assert output_file.exists()
        assert output_file.read_text() == "# Nuevo contenido"
    
    def test_is_processed_true(self):
        """Test verificar si archivo ha sido procesado (verdadero)."""
        # Crear PDF y archivo de extracción
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        extraction_file = self.temp_dir / "test_extraccion.md"
        extraction_file.write_text("Contenido")
        
        assert self.file_handler.is_processed(pdf_file) is True
    
    def test_is_processed_false(self):
        """Test verificar si archivo ha sido procesado (falso)."""
        # Crear solo PDF sin archivo de extracción
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        assert self.file_handler.is_processed(pdf_file) is False
    
    def test_get_extraction_file(self):
        """Test obtener ruta de archivo de extracción."""
        pdf_file = self.temp_dir / "documento.pdf"
        
        extraction_file = self.file_handler.get_extraction_file(pdf_file)
        
        assert extraction_file.parent == pdf_file.parent
        assert extraction_file.stem == "documento_extraccion"
        assert extraction_file.suffix == ".md"
    
    def test_get_file_size_existing(self):
        """Test obtener tamaño de archivo existente."""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("contenido de prueba")
        
        size = self.file_handler.get_file_size(test_file)
        
        assert "B" in size
        assert size != "0 B"
    
    def test_get_file_size_nonexistent(self):
        """Test obtener tamaño de archivo inexistente."""
        non_existent = self.temp_dir / "no_existe.txt"
        
        size = self.file_handler.get_file_size(non_existent)
        
        assert size == "0 B"
    
    def test_validate_pdf_file_valid(self):
        """Test validar PDF válido."""
        pdf_file = self.temp_dir / "valid.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContenido del PDF")
        
        assert self.file_handler.validate_pdf_file(pdf_file) is True
    
    def test_validate_pdf_file_invalid_extension(self):
        """Test validar archivo con extensión incorrecta."""
        txt_file = self.temp_dir / "not_pdf.txt"
        txt_file.write_text("No es un PDF")
        
        assert self.file_handler.validate_pdf_file(txt_file) is False
    
    def test_validate_pdf_file_invalid_header(self):
        """Test validar archivo PDF con header inválido."""
        fake_pdf = self.temp_dir / "fake.pdf"
        fake_pdf.write_text("No es un PDF real")
        
        assert self.file_handler.validate_pdf_file(fake_pdf) is False
    
    def test_validate_pdf_file_nonexistent(self):
        """Test validar PDF inexistente."""
        non_existent = self.temp_dir / "no_existe.pdf"
        
        assert self.file_handler.validate_pdf_file(non_existent) is False
    
    def test_clean_filename_basic(self):
        """Test limpiar nombre de archivo básico."""
        dirty_name = "archivo con espacios.pdf"
        clean_name = self.file_handler.clean_filename(dirty_name)
        
        assert " " not in clean_name
        assert "_" in clean_name
    
    def test_clean_filename_invalid_chars(self):
        """Test limpiar nombre con caracteres inválidos."""
        dirty_name = "archivo<>:\"/\\|?*.pdf"
        clean_name = self.file_handler.clean_filename(dirty_name)
        
        invalid_chars = '<>:"/\\|?*'
        assert not any(char in clean_name for char in invalid_chars)
    
    def test_clean_filename_too_long(self):
        """Test limpiar nombre muy largo."""
        long_name = "a" * 150 + ".pdf"
        clean_name = self.file_handler.clean_filename(long_name)
        
        assert len(clean_name) <= 100
        assert clean_name.endswith(".pdf")
    
    def test_backup_file(self):
        """Test crear respaldo de archivo."""
        original_file = self.temp_dir / "original.txt"
        original_content = "contenido original"
        original_file.write_text(original_content)
        
        backup_file = self.file_handler.backup_file(original_file)
        
        assert backup_file.exists()
        assert backup_file.read_text() == original_content
        assert backup_file.name.endswith(".bak")
    
    def test_backup_file_nonexistent(self):
        """Test respaldar archivo inexistente."""
        non_existent = self.temp_dir / "no_existe.txt"
        
        with pytest.raises(FileNotFoundError):
            self.file_handler.backup_file(non_existent)
    
    def test_get_processing_stats(self):
        """Test obtener estadísticas de procesamiento."""
        # Crear archivos de prueba
        pdf1 = self.temp_dir / "doc1.pdf"
        pdf2 = self.temp_dir / "doc2.pdf"
        pdf1.write_bytes(b"%PDF-1.4\nContent1")
        pdf2.write_bytes(b"%PDF-1.4\nContent2")
        
        # Crear archivo de extracción solo para uno
        extraction1 = self.temp_dir / "doc1_extraccion.md"
        extraction1.write_text("Extracción 1")
        
        stats = self.file_handler.get_processing_stats(self.temp_dir)
        
        assert stats["total_pdfs"] == 2
        assert stats["processed"] == 1
        assert stats["pending"] == 1
        assert stats["completion_rate"] == 0.5
    
    def test_get_processing_stats_nonexistent_directory(self):
        """Test estadísticas para directorio inexistente."""
        non_existent = self.temp_dir / "no_existe"
        
        with pytest.raises(FileNotFoundError):
            self.file_handler.get_processing_stats(non_existent)


@pytest.fixture
def sample_pdf_bytes():
    """Fixture para contenido de PDF de muestra."""
    return b"%PDF-1.4\n%\xc7\xec\x8f\xa2\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj"