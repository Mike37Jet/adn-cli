"""
Manejador de archivos para ADN CLI.
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from .config import ConfigManager
from .logger import get_logger
from .template_engine import TemplateEngine

logger = get_logger(__name__)


class FileHandler:
    """Manejador de archivos para procesamiento de PDFs y generación de extracciones."""
    
    def __init__(self):
        """Inicializar el manejador de archivos."""
        self.config_manager = ConfigManager()
        self.template_engine = TemplateEngine()
    
    def find_pdf_files(self, directory: Path, pattern: str = "*.pdf") -> List[Path]:
        """
        Buscar archivos PDF en un directorio.
        
        Args:
            directory: Directorio a buscar
            pattern: Patrón de búsqueda (ej: "*.pdf", "report_*.pdf")
            
        Returns:
            List[Path]: Lista de archivos PDF encontrados
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"La ruta no es un directorio: {directory}")
        
        # Buscar archivos usando glob
        pdf_files = list(directory.glob(pattern))
        
        # Filtrar solo archivos (no directorios) y que terminen en .pdf
        pdf_files = [
            f for f in pdf_files 
            if f.is_file() and f.suffix.lower() == '.pdf'
        ]
        
        logger.debug(f"Encontrados {len(pdf_files)} archivos PDF en {directory}")
        return pdf_files
    
    def generate_extraction_file(
        self,
        pdf_file: Path,
        output_dir: Optional[Path] = None,
        template_name: Optional[str] = None,
        force: bool = False
    ) -> Path:
        """
        Generar archivo de extracción para un PDF.
        
        Args:
            pdf_file: Archivo PDF fuente
            output_dir: Directorio de salida (opcional)
            template_name: Nombre del template a usar (opcional)
            force: Sobrescribir archivo existente
            
        Returns:
            Path: Ruta del archivo de extracción generado
            
        Raises:
            FileNotFoundError: Si el archivo PDF no existe
            FileExistsError: Si el archivo de salida ya existe y force=False
        """
        if not pdf_file.exists():
            raise FileNotFoundError(f"Archivo PDF no encontrado: {pdf_file}")
        
        # Configurar directorio de salida
        if output_dir is None:
            output_dir = Path(self.config_manager.get_config_value("default_output_dir", "."))
            if not output_dir.is_absolute():
                output_dir = pdf_file.parent / output_dir
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre del archivo de salida
        output_file = self._generate_output_filename(pdf_file, output_dir)
        
        # Verificar si ya existe
        if output_file.exists() and not force:
            raise FileExistsError(f"El archivo ya existe: {output_file}")
        
        # Obtener template a usar
        if template_name is None:
            template_name = self.config_manager.get_config_value("default_template", "default")
        
        # Renderizar contenido
        try:
            content = self.template_engine.render_template(
                template_name=template_name,
                pdf_file=pdf_file
            )
            
            # Escribir archivo
            output_file.write_text(content, encoding='utf-8')
            
            logger.info(f"Archivo de extracción generado: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error generando archivo de extracción para {pdf_file}: {e}")
            raise
    
    def is_processed(self, pdf_file: Path) -> bool:
        """
        Verificar si un archivo PDF ya ha sido procesado.
        
        Args:
            pdf_file: Archivo PDF a verificar
            
        Returns:
            bool: True si ya ha sido procesado
        """
        expected_output = self._generate_output_filename(pdf_file, pdf_file.parent)
        return expected_output.exists()
    
    def get_extraction_file(self, pdf_file: Path, output_dir: Optional[Path] = None) -> Path:
        """
        Obtener la ruta del archivo de extracción para un PDF.
        
        Args:
            pdf_file: Archivo PDF fuente
            output_dir: Directorio de salida (opcional)
            
        Returns:
            Path: Ruta del archivo de extracción
        """
        if output_dir is None:
            output_dir = pdf_file.parent
        
        return self._generate_output_filename(pdf_file, Path(output_dir))
    
    def get_file_size(self, file_path: Path) -> str:
        """
        Obtener el tamaño de un archivo en formato legible.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            str: Tamaño formateado (ej: "1.5 MB")
        """
        if not file_path.exists():
            return "0 B"
        
        size_bytes = file_path.stat().st_size
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} PB"
    
    def validate_pdf_file(self, file_path: Path) -> bool:
        """
        Validar que un archivo es un PDF válido.
        
        Args:
            file_path: Ruta del archivo a validar
            
        Returns:
            bool: True si es un PDF válido
        """
        if not file_path.exists():
            return False
        
        if not file_path.is_file():
            return False
        
        if file_path.suffix.lower() != '.pdf':
            return False
        
        # Verificación básica del header PDF
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                return header.startswith(b'%PDF-')
        except Exception:
            return False
    
    def clean_filename(self, filename: str) -> str:
        """
        Limpiar nombre de archivo removiendo caracteres problemáticos.
        
        Args:
            filename: Nombre de archivo original
            
        Returns:
            str: Nombre de archivo limpio
        """
        # Caracteres problemáticos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        
        cleaned = filename
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
        
        # Remover espacios múltiples y reemplazar por guiones bajos
        cleaned = ' '.join(cleaned.split())
        cleaned = cleaned.replace(' ', '_')
        
        # Limitar longitud
        max_length = self.config_manager.get_config_value("max_filename_length", 100)
        if len(cleaned) > max_length:
            name, ext = os.path.splitext(cleaned)
            cleaned = name[:max_length - len(ext)] + ext
        
        return cleaned
    
    def backup_file(self, file_path: Path) -> Path:
        """
        Crear respaldo de un archivo.
        
        Args:
            file_path: Archivo a respaldar
            
        Returns:
            Path: Ruta del archivo de respaldo
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        backup_path = file_path.with_suffix(f'{file_path.suffix}.bak')
        
        # Si ya existe un backup, agregar número
        counter = 1
        while backup_path.exists():
            backup_path = file_path.with_suffix(f'{file_path.suffix}.bak.{counter}')
            counter += 1
        
        backup_path.write_bytes(file_path.read_bytes())
        
        logger.info(f"Respaldo creado: {backup_path}")
        return backup_path
    
    def _generate_output_filename(self, pdf_file: Path, output_dir: Path) -> Path:
        """
        Generar nombre del archivo de salida.
        
        Args:
            pdf_file: Archivo PDF fuente
            output_dir: Directorio de salida
            
        Returns:
            Path: Ruta completa del archivo de salida
        """
        suffix = self.config_manager.get_config_value("output_suffix", "_extraccion")
        base_name = pdf_file.stem
        
        # Limpiar nombre base
        clean_base = self.clean_filename(base_name)
        
        # Generar nombre final
        output_name = f"{clean_base}{suffix}.md"
        
        return output_dir / output_name
    
    def get_processing_stats(self, directory: Path) -> dict:
        """
        Obtener estadísticas de procesamiento para un directorio.
        
        Args:
            directory: Directorio a analizar
            
        Returns:
            dict: Estadísticas de procesamiento
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {directory}")
        
        pdf_files = self.find_pdf_files(directory)
        processed_files = [f for f in pdf_files if self.is_processed(f)]
        pending_files = [f for f in pdf_files if not self.is_processed(f)]
        
        total_size = sum(f.stat().st_size for f in pdf_files if f.exists())
        processed_size = sum(f.stat().st_size for f in processed_files if f.exists())
        
        return {
            "total_pdfs": len(pdf_files),
            "processed": len(processed_files),
            "pending": len(pending_files),
            "total_size": total_size,
            "processed_size": processed_size,
            "completion_rate": len(processed_files) / len(pdf_files) if pdf_files else 0,
            "pdf_files": pdf_files,
            "processed_files": processed_files,
            "pending_files": pending_files,
        }