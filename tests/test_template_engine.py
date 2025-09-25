"""
Tests unitarios para el motor de templates.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from adn.utils.template_engine import TemplateEngine


class TestTemplateEngine:
    """Tests para el motor de templates."""
    
    def setup_method(self):
        """Configurar cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.template_engine = TemplateEngine()
        
        # Patchear directorio de templates para usar temporal
        self.template_engine.templates_dir = self.temp_dir
        
        # Recrear entorno Jinja2 con nuevo directorio
        from jinja2 import Environment, FileSystemLoader
        self.template_engine.env = Environment(
            loader=FileSystemLoader(str(self.temp_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Reagregar filtros personalizados
        self.template_engine.env.filters['dateformat'] = self.template_engine._dateformat_filter
        self.template_engine.env.filters['filesize'] = self.template_engine._filesize_filter
    
    def teardown_method(self):
        """Limpiar después de cada test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_render_template_default(self):
        """Test renderizar template por defecto."""
        # Crear template de prueba
        template_content = "# {{ nombre_archivo }} extracción\nGenerado: {{ fecha_actual }}"
        template_file = self.temp_dir / "default.md"
        template_file.write_text(template_content)
        
        # Crear PDF de prueba
        pdf_file = Path("documento.pdf")
        
        # Renderizar
        result = self.template_engine.render_template(
            template_name="default",
            pdf_file=pdf_file
        )
        
        assert "documento extracción" in result
        assert "Generado:" in result
    
    def test_render_template_with_variables(self):
        """Test renderizar template con variables adicionales."""
        template_content = "Archivo: {{ nombre_archivo }}\nAutor: {{ autor }}"
        template_file = self.temp_dir / "custom.md"
        template_file.write_text(template_content)
        
        pdf_file = Path("test.pdf")
        
        result = self.template_engine.render_template(
            template_name="custom",
            pdf_file=pdf_file,
            autor="Juan Pérez"
        )
        
        assert "Archivo: test" in result
        assert "Autor: Juan Pérez" in result
    
    def test_render_template_nonexistent(self):
        """Test renderizar template inexistente."""
        pdf_file = Path("test.pdf")
        
        with pytest.raises(Exception):  # Jinja2 lanzará TemplateNotFound
            self.template_engine.render_template(
                template_name="no_existe",
                pdf_file=pdf_file
            )
    
    def test_get_template_content_existing(self):
        """Test obtener contenido de template existente."""
        template_content = "# Template de prueba\n{{ nombre_archivo }}"
        template_file = self.temp_dir / "test.md"
        template_file.write_text(template_content)
        
        content = self.template_engine.get_template_content("test")
        
        assert content == template_content
    
    def test_get_template_content_default_fallback(self):
        """Test obtener contenido de template por defecto cuando no existe."""
        content = self.template_engine.get_template_content("default")
        
        # Debería devolver el contenido del template por defecto
        assert "extracción" in content
        assert "{{ nombre_archivo }}" in content
    
    def test_get_template_content_nonexistent(self):
        """Test obtener contenido de template inexistente."""
        with pytest.raises(FileNotFoundError):
            self.template_engine.get_template_content("no_existe")
    
    def test_list_templates(self):
        """Test listar templates disponibles."""
        # Crear algunos templates
        (self.temp_dir / "template1.md").write_text("Template 1")
        (self.temp_dir / "template2.md").write_text("Template 2")
        (self.temp_dir / "no_template.txt").write_text("No es template")
        
        templates = self.template_engine.list_templates()
        
        assert "template1" in templates
        assert "template2" in templates
        assert "no_template" not in templates  # Solo archivos .md
        assert len(templates) == 2
    
    def test_list_templates_empty_directory(self):
        """Test listar templates en directorio vacío."""
        templates = self.template_engine.list_templates()
        
        assert templates == []
    
    def test_create_template(self):
        """Test crear nuevo template."""
        content = "# Nuevo template\n{{ nombre_archivo }}"
        
        template_file = self.template_engine.create_template("nuevo", content)
        
        assert template_file.exists()
        assert template_file.read_text() == content
        assert template_file.name == "nuevo.md"
    
    def test_create_template_exists_no_force(self):
        """Test crear template cuando ya existe sin force."""
        existing_file = self.temp_dir / "existente.md"
        existing_file.write_text("Contenido existente")
        
        with pytest.raises(FileExistsError):
            self.template_engine.create_template("existente", "Nuevo contenido")
    
    def test_create_template_exists_with_force(self):
        """Test crear template cuando ya existe con force."""
        existing_file = self.temp_dir / "existente.md"
        existing_file.write_text("Contenido existente")
        
        new_content = "Contenido nuevo"
        template_file = self.template_engine.create_template(
            "existente", 
            new_content, 
            force=True
        )
        
        assert template_file.read_text() == new_content
    
    def test_prepare_context_with_pdf(self):
        """Test preparar contexto con archivo PDF."""
        # Crear PDF de prueba
        pdf_file = self.temp_dir / "documento.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\nContent")
        
        context = self.template_engine._prepare_context(pdf_file)
        
        assert context["nombre_archivo"] == "documento"
        assert context["nombre_completo"] == "documento.pdf"
        assert context["ruta_archivo"] == str(pdf_file)
        assert "fecha_actual" in context
        assert "version_adn" in context
    
    def test_prepare_context_without_pdf(self):
        """Test preparar contexto sin archivo PDF."""
        context = self.template_engine._prepare_context(None)
        
        assert "fecha_actual" in context
        assert "version_adn" in context
        assert "nombre_archivo" not in context
    
    def test_prepare_context_with_extra_vars(self):
        """Test preparar contexto con variables adicionales."""
        pdf_file = Path("test.pdf")
        
        context = self.template_engine._prepare_context(
            pdf_file,
            autor="Juan",
            categoria="Investigación"
        )
        
        assert context["autor"] == "Juan"
        assert context["categoria"] == "Investigación"
        assert context["nombre_archivo"] == "test"
    
    def test_dateformat_filter(self):
        """Test filtro personalizado de fecha."""
        from datetime import datetime
        
        test_date = datetime(2024, 3, 15, 14, 30, 0)
        
        # Formato por defecto
        result = self.template_engine._dateformat_filter(test_date)
        assert result == "15/03/2024"
        
        # Formato personalizado
        result = self.template_engine._dateformat_filter(test_date, "%Y-%m-%d")
        assert result == "2024-03-15"
    
    def test_dateformat_filter_invalid_date(self):
        """Test filtro de fecha con objeto inválido."""
        result = self.template_engine._dateformat_filter("not a date")
        assert result == "not a date"
    
    def test_filesize_filter(self):
        """Test filtro personalizado de tamaño de archivo."""
        # Bytes
        assert self.template_engine._filesize_filter(500) == "500.0 B"
        
        # KB
        assert self.template_engine._filesize_filter(1500) == "1.5 KB"
        
        # MB
        assert self.template_engine._filesize_filter(2048000) == "2.0 MB"
        
        # GB
        assert self.template_engine._filesize_filter(3221225472) == "3.0 GB"
    
    def test_filesize_filter_invalid_size(self):
        """Test filtro de tamaño con valor inválido."""
        result = self.template_engine._filesize_filter("invalid")
        assert result == "invalid"
    
    def test_filters_in_template(self):
        """Test usar filtros personalizados en template."""
        from datetime import datetime
        
        template_content = """
        Fecha: {{ fecha_actual | dateformat('%d/%m/%Y') }}
        Tamaño: {{ tamaño_archivo | filesize }}
        """
        
        template_file = self.temp_dir / "filters.md"
        template_file.write_text(template_content)
        
        # Crear PDF de prueba
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n" + b"x" * 1500)  # 1.5KB aprox
        
        result = self.template_engine.render_template(
            template_name="filters",
            pdf_file=pdf_file
        )
        
        assert "Fecha:" in result
        assert "Tamaño:" in result
        assert "KB" in result or "B" in result
    
    def test_ensure_default_template_created(self):
        """Test que el template por defecto se crea automáticamente."""
        # Limpiar directorio
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir.mkdir()
        
        # Crear nueva instancia que debería crear el template por defecto
        new_engine = TemplateEngine()
        new_engine.templates_dir = self.temp_dir
        new_engine._ensure_default_template()
        
        default_template = self.temp_dir / "default.md"
        assert default_template.exists()
        
        content = default_template.read_text()
        assert "extracción" in content
        assert "{{ nombre_archivo }}" in content