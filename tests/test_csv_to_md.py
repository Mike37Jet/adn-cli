"""
Tests para la funcionalidad CSV to Markdown.
"""

import csv
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from adn.commands.csv_to_md import CSVToMarkdownProcessor


class TestCSVToMarkdownProcessor:
    """Tests para el procesador CSV to Markdown."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.test_output_dir = Path("test_output")
        self.processor = CSVToMarkdownProcessor(self.test_output_dir)
    
    def test_init(self):
        """Test inicialización del procesador."""
        assert self.processor.output_dir == self.test_output_dir
        assert self.processor.REQUIRED_COLUMNS == {'source', 'doi', 'title', 'abstract'}
    
    def test_validate_csv_file_not_found(self):
        """Test validación con archivo que no existe."""
        non_existent_file = Path("archivo_que_no_existe.csv")
        
        with pytest.raises(FileNotFoundError) as excinfo:
            self.processor.validate_csv(non_existent_file)
        
        assert "Archivo CSV no encontrado" in str(excinfo.value)
    
    def test_validate_csv_not_a_file(self, tmp_path):
        """Test validación con directorio en lugar de archivo."""
        directory = tmp_path / "directorio"
        directory.mkdir()
        
        with pytest.raises(ValueError) as excinfo:
            self.processor.validate_csv(directory)
        
        assert "La ruta no apunta a un archivo" in str(excinfo.value)
    
    def test_validate_csv_missing_columns(self, tmp_path):
        """Test validación con columnas faltantes."""
        csv_file = tmp_path / "test.csv"
        csv_content = "wrong_column,another_column\nvalue1,value2\n"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        with pytest.raises(ValueError) as excinfo:
            self.processor.validate_csv(csv_file)
        
        assert "Columnas requeridas faltantes" in str(excinfo.value)
        assert "abstract" in str(excinfo.value)
        assert "doi" in str(excinfo.value)
        assert "source" in str(excinfo.value)
        assert "title" in str(excinfo.value)
    
    def test_validate_csv_valid_file(self, tmp_path):
        """Test validación con archivo CSV válido."""
        csv_file = tmp_path / "test.csv"
        csv_content = "source,doi,title,abstract,extra_column\nvalue1,value2,value3,value4,value5\n"
        csv_file.write_text(csv_content, encoding='utf-8')
        
        columns = self.processor.validate_csv(csv_file)
        
        assert set(columns) >= self.processor.REQUIRED_COLUMNS
        assert "extra_column" in columns
    
    def test_read_csv_data_valid_file(self, tmp_path):
        """Test lectura de datos CSV válidos."""
        csv_file = tmp_path / "test.csv"
        csv_content = """source,doi,title,abstract
"Test Source","10.1234/test","Test Title","Test Abstract"
"Another Source","10.1234/another","Another Title","Another Abstract"
"""
        csv_file.write_text(csv_content, encoding='utf-8')
        
        data = self.processor.read_csv_data(csv_file)
        
        assert len(data) == 2
        assert data[0]['source'] == 'Test Source'
        assert data[0]['doi'] == '10.1234/test'
        assert data[1]['title'] == 'Another Title'
        assert data[1]['abstract'] == 'Another Abstract'
    
    def test_read_csv_data_with_missing_values(self, tmp_path):
        """Test lectura de datos CSV con valores faltantes."""
        csv_file = tmp_path / "test.csv"
        csv_content = """source,doi,title,abstract
"Test Source",,"Test Title","Test Abstract"
,,"Missing Everything",
"""
        csv_file.write_text(csv_content, encoding='utf-8')
        
        data = self.processor.read_csv_data(csv_file)
        
        assert len(data) == 2
        assert data[0]['source'] == 'Test Source'
        assert data[0]['doi'] == ''
        assert data[1]['source'] == ''
        assert data[1]['title'] == 'Missing Everything'
    
    def test_create_markdown_content(self):
        """Test creación de contenido Markdown."""
        record = {
            'source': 'Test Journal',
            'doi': '10.1234/test.001',
            'title': 'Test Article',
            'abstract': 'This is a test abstract'
        }
        
        content = self.processor.create_markdown_content(record)
        
        expected_content = """---
source: Test Journal
doi: 10.1234/test.001
title: Test Article
abstract: This is a test abstract
estado:
  - procesado
tags:
  - documento
  - investigacion
---"""
        
        assert content == expected_content
    
    def test_create_markdown_content_with_missing_values(self):
        """Test creación de contenido Markdown con valores faltantes."""
        record = {
            'source': 'Test Journal',
            'doi': '',
            'title': 'Test Article',
            'abstract': ''
        }
        
        content = self.processor.create_markdown_content(record)
        
        expected_content = """---
source: Test Journal
doi: 
title: Test Article
abstract: 
estado:
  - procesado
tags:
  - documento
  - investigacion
---"""
        
        assert content == expected_content
    
    def test_create_markdown_content_missing_keys(self):
        """Test creación de contenido con claves faltantes en el registro."""
        record = {
            'source': 'Test Journal',
            'title': 'Test Article'
            # doi y abstract faltantes
        }
        
        content = self.processor.create_markdown_content(record)
        
        expected_content = """---
source: Test Journal
doi: 
title: Test Article
abstract: 
estado:
  - procesado
tags:
  - documento
  - investigacion
---"""
        
        assert content == expected_content
    
    def test_process_csv_integration(self, tmp_path):
        """Test integración completa del procesamiento CSV."""
        # Crear archivo CSV de prueba
        csv_file = tmp_path / "test.csv"
        csv_content = """source,doi,title,abstract
"Journal A","10.1234/a","Article A","Abstract A"
"Journal B","10.1234/b","Article B","Abstract B"
"""
        csv_file.write_text(csv_content, encoding='utf-8')
        
        # Configurar directorio de salida
        output_dir = tmp_path / "output"
        processor = CSVToMarkdownProcessor(output_dir)
        
        # Procesar CSV
        files_created = processor.process_csv(csv_file)
        
        # Verificar resultados
        assert files_created == 2
        assert (output_dir / "001.md").exists()
        assert (output_dir / "002.md").exists()
        
        # Verificar contenido del primer archivo
        content_001 = (output_dir / "001.md").read_text(encoding='utf-8')
        assert "source: Journal A" in content_001
        assert "doi: 10.1234/a" in content_001
        assert "title: Article A" in content_001
        assert "abstract: Abstract A" in content_001
        
        # Verificar contenido del segundo archivo
        content_002 = (output_dir / "002.md").read_text(encoding='utf-8')
        assert "source: Journal B" in content_002
        assert "doi: 10.1234/b" in content_002
    
    def test_process_csv_with_start_number(self, tmp_path):
        """Test procesamiento con número inicial personalizado."""
        # Crear archivo CSV de prueba
        csv_file = tmp_path / "test.csv"
        csv_content = """source,doi,title,abstract
"Journal A","10.1234/a","Article A","Abstract A"
"""
        csv_file.write_text(csv_content, encoding='utf-8')
        
        # Configurar directorio de salida
        output_dir = tmp_path / "output"
        processor = CSVToMarkdownProcessor(output_dir)
        
        # Procesar CSV con número inicial 10
        files_created = processor.process_csv(csv_file, start_number=10)
        
        # Verificar resultados
        assert files_created == 1
        assert (output_dir / "010.md").exists()
        assert not (output_dir / "001.md").exists()
    
    def test_process_csv_empty_file(self, tmp_path):
        """Test procesamiento con archivo CSV vacío."""
        csv_file = tmp_path / "empty.csv"
        csv_content = "source,doi,title,abstract\n"  # Solo headers
        csv_file.write_text(csv_content, encoding='utf-8')
        
        output_dir = tmp_path / "output"
        processor = CSVToMarkdownProcessor(output_dir)
        
        files_created = processor.process_csv(csv_file)
        
        assert files_created == 0
        assert not any(output_dir.glob("*.md"))