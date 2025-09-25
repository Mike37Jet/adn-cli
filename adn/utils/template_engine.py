"""
Motor de templates para ADN CLI usando Jinja2.
"""

import datetime
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, Template

from .config import ConfigManager
from .logger import get_logger

logger = get_logger(__name__)


class TemplateEngine:
    """Motor de templates para generar archivos de extracción."""
    
    def __init__(self):
        """Inicializar el motor de templates."""
        self.config_manager = ConfigManager()
        self.templates_dir = self.config_manager.templates_dir
        
        # Asegurar que el directorio de templates existe
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear template por defecto si no existe
        self._ensure_default_template()
        
        # Configurar entorno Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,  # No escapar para Markdown
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Agregar filtros personalizados
        self.env.filters['dateformat'] = self._dateformat_filter
        self.env.filters['filesize'] = self._filesize_filter
    
    def render_template(
        self,
        template_name: str = "default",
        pdf_file: Optional[Path] = None,
        **kwargs
    ) -> str:
        """
        Renderizar un template con los datos proporcionados.
        
        Args:
            template_name: Nombre del template a usar
            pdf_file: Archivo PDF fuente
            **kwargs: Variables adicionales para el template
        
        Returns:
            str: Contenido renderizado del template
        """
        try:
            # Cargar template
            template_file = f"{template_name}.md"
            template = self.env.get_template(template_file)
            
            # Preparar contexto de variables
            context = self._prepare_context(pdf_file, **kwargs)
            
            # Renderizar template
            rendered = template.render(**context)
            
            logger.debug(f"Template '{template_name}' renderizado correctamente")
            return rendered
            
        except Exception as e:
            logger.error(f"Error renderizando template '{template_name}': {e}")
            raise
    
    def get_template_content(self, template_name: str = "default") -> str:
        """
        Obtener el contenido crudo de un template.
        
        Args:
            template_name: Nombre del template
            
        Returns:
            str: Contenido del template
        """
        template_file = self.templates_dir / f"{template_name}.md"
        
        if not template_file.exists():
            if template_name == "default":
                return self._get_default_template_content()
            else:
                raise FileNotFoundError(f"Template no encontrado: {template_name}")
        
        return template_file.read_text(encoding='utf-8')
    
    def list_templates(self) -> list[str]:
        """
        Listar todos los templates disponibles.
        
        Returns:
            list: Lista de nombres de templates disponibles
        """
        templates = []
        
        for template_file in self.templates_dir.glob("*.md"):
            template_name = template_file.stem
            templates.append(template_name)
        
        return sorted(templates)
    
    def create_template(self, name: str, content: str, force: bool = False) -> Path:
        """
        Crear un nuevo template.
        
        Args:
            name: Nombre del template
            content: Contenido del template
            force: Sobrescribir si existe
            
        Returns:
            Path: Ruta del archivo de template creado
        """
        template_file = self.templates_dir / f"{name}.md"
        
        if template_file.exists() and not force:
            raise FileExistsError(f"El template '{name}' ya existe")
        
        template_file.write_text(content, encoding='utf-8')
        logger.info(f"Template creado: {template_file}")
        
        return template_file
    
    def _prepare_context(self, pdf_file: Optional[Path], **kwargs) -> Dict:
        """
        Preparar el contexto de variables para el template.
        
        Args:
            pdf_file: Archivo PDF fuente
            **kwargs: Variables adicionales
            
        Returns:
            Dict: Contexto de variables
        """
        context = {
            'fecha_actual': datetime.datetime.now(),
            'version_adn': '1.0.0',  # Podría venir de __init__.py
        }
        
        if pdf_file:
            context.update({
                'nombre_archivo': pdf_file.stem,
                'nombre_completo': pdf_file.name,
                'ruta_archivo': str(pdf_file),
                'tamaño_archivo': pdf_file.stat().st_size if pdf_file.exists() else 0,
            })
        
        # Agregar variables adicionales
        context.update(kwargs)
        
        return context
    
    def _ensure_default_template(self) -> None:
        """Asegurar que existe el template por defecto."""
        default_template = self.templates_dir / "default.md"
        
        if not default_template.exists():
            content = self._get_default_template_content()
            default_template.write_text(content, encoding='utf-8')
            logger.info("Template por defecto creado")
    
    def _get_default_template_content(self) -> str:
        """
        Obtener el contenido del template por defecto.
        
        Returns:
            str: Contenido del template por defecto
        """
        return '''# {{ nombre_archivo }} extracción

## Metadatos
- **Archivo fuente**: {{ nombre_completo }}
- **Fecha de creación**: {{ fecha_actual.strftime("%d/%m/%Y %H:%M") }}
- **Generado por**: ADN CLI v{{ version_adn }}
- **Tamaño del archivo**: {{ tamaño_archivo | filesize }}

## Resumen ejecutivo
[Espacio para resumen]

## Puntos clave
- 
- 
- 

## Citas importantes
> 

## Notas adicionales
[Espacio para notas]

## Referencias
[Espacio para referencias]

## Estructura del documento
- [ ] Introducción revisada
- [ ] Metodología analizada
- [ ] Resultados extraídos
- [ ] Conclusiones resumidas

## Tags
`{{ nombre_archivo }}` `extracción` `pdf` `notas`

---
**annotation-target**: {{ nombre_completo }}
**generated**: {{ fecha_actual.isoformat() }}
'''
    
    def _dateformat_filter(self, date, format_str='%d/%m/%Y'):
        """Filtro personalizado para formatear fechas."""
        if hasattr(date, 'strftime'):
            return date.strftime(format_str)
        return str(date)
    
    def _filesize_filter(self, size_bytes):
        """Filtro personalizado para formatear tamaños de archivo."""
        if not isinstance(size_bytes, (int, float)):
            return str(size_bytes)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"