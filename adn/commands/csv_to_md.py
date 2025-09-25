"""
Comando 'csv-to-md' para convertir archivos CSV a archivos Markdown individuales.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, TaskID, track

from ..utils import get_logger
from ..utils.template_engine import TemplateEngine

console = Console()
logger = get_logger(__name__)

# Sub-aplicación para comandos 'csv-to-md'
csv_to_md_router = typer.Typer(
    help="Comandos para convertir CSV a archivos Markdown",
    rich_markup_mode="rich"
)


class CSVToMarkdownProcessor:
    """Procesador para convertir archivos CSV a archivos Markdown individuales."""
    
    REQUIRED_COLUMNS = {'source', 'doi', 'title', 'abstract'}
    
    def __init__(self, output_dir: Path):
        """
        Inicializar el procesador.
        
        Args:
            output_dir: Directorio donde se guardarán los archivos Markdown
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_engine = TemplateEngine()
        logger.debug(f"Procesador inicializado con directorio de salida: {self.output_dir}")
    
    def validate_csv(self, csv_file: Path) -> List[str]:
        """
        Validar que el archivo CSV tenga las columnas requeridas.
        
        Args:
            csv_file: Ruta al archivo CSV
            
        Returns:
            List[str]: Lista de columnas encontradas
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si las columnas requeridas no están presentes
        """
        if not csv_file.exists():
            raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_file}")
        
        if not csv_file.is_file():
            raise ValueError(f"La ruta no apunta a un archivo: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8-sig', newline='') as file:
                reader = csv.DictReader(file)
                columns = set(reader.fieldnames or [])
                
                # Verificar columnas requeridas
                missing_columns = self.REQUIRED_COLUMNS - columns
                if missing_columns:
                    raise ValueError(
                        f"Columnas requeridas faltantes: {', '.join(sorted(missing_columns))}"
                    )
                
                logger.info(f"CSV validado correctamente. Columnas encontradas: {', '.join(sorted(columns))}")
                return list(columns)
                
        except UnicodeDecodeError:
            # Intentar con diferentes encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(csv_file, 'r', encoding=encoding, newline='') as file:
                        reader = csv.DictReader(file)
                        columns = set(reader.fieldnames or [])
                        
                        missing_columns = self.REQUIRED_COLUMNS - columns
                        if missing_columns:
                            raise ValueError(
                                f"Columnas requeridas faltantes: {', '.join(sorted(missing_columns))}"
                            )
                        
                        logger.info(f"CSV validado con encoding {encoding}. Columnas: {', '.join(sorted(columns))}")
                        return list(columns)
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("No se pudo leer el archivo CSV con ningún encoding soportado")
        
        except ValueError:
            # Re-lanzar ValueError sin modificar el mensaje
            raise
        except Exception as e:
            raise ValueError(f"Error al leer el archivo CSV: {e}")
    
    def read_csv_data(self, csv_file: Path) -> List[Dict[str, str]]:
        """
        Leer los datos del archivo CSV.
        
        Args:
            csv_file: Ruta al archivo CSV
            
        Returns:
            List[Dict[str, str]]: Lista de registros del CSV
        """
        data = []
        
        # Intentar diferentes encodings
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', encoding=encoding, newline='') as file:
                    reader = csv.DictReader(file)
                    data = [row for row in reader]
                    logger.info(f"CSV leído correctamente con encoding {encoding}. {len(data)} registros encontrados.")
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error al leer CSV con encoding {encoding}: {e}")
                continue
        
        if not data:
            raise ValueError("No se pudo leer el archivo CSV con ningún encoding soportado")
        
        return data
    
    def create_markdown_content(self, record: Dict[str, str]) -> str:
        """
        Crear el contenido Markdown para un registro usando template.
        
        Args:
            record: Diccionario con los datos del registro
            
        Returns:
            str: Contenido del archivo Markdown
        """
        # Obtener valores de las columnas requeridas, usando cadena vacía si no existe
        source = record.get('source', '').strip()
        doi = record.get('doi', '').strip()
        title = record.get('title', '').strip()
        abstract = record.get('abstract', '').strip()
        
        # Procesar el abstract para manejar saltos de línea con indentación correcta
        if abstract:
            # Dividir por líneas y agregar indentación de 2 espacios a cada línea
            abstract_lines = abstract.split('\n')
            abstract_formatted = '\n'.join(f'  {line.strip()}' if line.strip() else '  ' for line in abstract_lines)
        else:
            abstract_formatted = '  '
        
        # Usar el template engine para generar el contenido
        try:
            content = self.template_engine.render_template(
                template_name="csv_record",
                source=source,
                doi=doi,
                title=title,
                abstract_formatted=abstract_formatted
            )
            return content
        except Exception as e:
            logger.warning(f"Error usando template csv_record, usando formato por defecto: {e}")
            # Fallback al formato hardcodeado si hay problemas con el template
            content = f"""---
source: {source}
doi: {doi}
title: "{title}"
abstract: |
{abstract_formatted}
estado:
  - procesado
tags:
  - documento
  - investigacion
---"""
            return content
    
    def process_csv(self, csv_file: Path, start_number: int = 1) -> int:
        """
        Procesar el archivo CSV y generar archivos Markdown.
        
        Args:
            csv_file: Ruta al archivo CSV
            start_number: Número inicial para la nomenclatura de archivos
            
        Returns:
            int: Número de archivos generados
        """
        # Validar CSV
        self.validate_csv(csv_file)
        
        # Leer datos
        data = self.read_csv_data(csv_file)
        
        if not data:
            console.print("[yellow]No se encontraron registros en el archivo CSV[/yellow]")
            return 0
        
        # Procesar registros con barra de progreso
        files_created = 0
        
        for i, record in enumerate(track(data, description="Procesando registros...")):
            try:
                # Generar nombre de archivo con formato de 3 dígitos
                file_number = start_number + i
                filename = f"{file_number:03d}.md"
                output_file = self.output_dir / filename
                
                # Crear contenido
                content = self.create_markdown_content(record)
                
                # Escribir archivo
                output_file.write_text(content, encoding='utf-8')
                files_created += 1
                
                logger.debug(f"Archivo creado: {filename}")
                
            except Exception as e:
                logger.error(f"Error procesando registro {i + 1}: {e}")
                console.print(f"[red]Error procesando registro {i + 1}: {e}[/red]")
                continue
        
        return files_created


@csv_to_md_router.command("convert")
def convert_csv_to_markdown(
    csv_file: Path = typer.Argument(..., help="Archivo CSV a procesar"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida para archivos Markdown (por defecto: directorio actual)"
    ),
    start_number: int = typer.Option(
        1, "--start-number", "-s", help="Número inicial para la nomenclatura de archivos"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Sobrescribir archivos existentes"
    ),
) -> None:
    """
    Convertir archivo CSV a archivos Markdown individuales.
    
    El archivo CSV debe contener las siguientes columnas obligatorias:
    - source: Fuente de la información
    - doi: Identificador único del documento  
    - title: Título del artículo/documento
    - abstract: Resumen del contenido
    
    Los archivos se numerarán secuencialmente: 001.md, 002.md, 003.md, etc.
    """
    
    # Configurar directorio de salida
    target_output_dir = output_dir or Path.cwd()
    
    # Verificar si el directorio de salida tiene archivos .md existentes
    if not force:
        existing_md_files = list(target_output_dir.glob("*.md"))
        if existing_md_files:
            console.print(f"[yellow]Advertencia: Se encontraron {len(existing_md_files)} archivos .md existentes en {target_output_dir}[/yellow]")
            confirm = typer.confirm("¿Desea continuar? (Los archivos existentes podrían ser sobrescritos)")
            if not confirm:
                console.print("[yellow]Operación cancelada[/yellow]")
                raise typer.Exit(0)
    
    try:
        # Crear procesador
        processor = CSVToMarkdownProcessor(target_output_dir)
        
        # Mostrar información inicial
        console.print(f"[blue]Procesando archivo CSV:[/blue] {csv_file}")
        console.print(f"[blue]Directorio de salida:[/blue] {target_output_dir}")
        console.print(f"[blue]Número inicial:[/blue] {start_number}")
        
        # Procesar archivo
        files_created = processor.process_csv(csv_file, start_number)
        
        # Mostrar resumen
        if files_created > 0:
            console.print(f"\n[green]✓ Procesamiento completado exitosamente[/green]")
            console.print(f"[green]Archivos generados:[/green] {files_created}")
            console.print(f"[green]Directorio de salida:[/green] {target_output_dir}")
            
            # Mostrar algunos archivos generados como ejemplo
            md_files = sorted(target_output_dir.glob("*.md"))
            if md_files:
                console.print(f"\n[blue]Archivos generados (ejemplos):[/blue]")
                for md_file in md_files[:5]:  # Mostrar solo los primeros 5
                    console.print(f"  • {md_file.name}")
                if len(md_files) > 5:
                    console.print(f"  ... y {len(md_files) - 5} más")
        else:
            console.print("[yellow]No se generaron archivos[/yellow]")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    except ValueError as e:
        console.print(f"[red]Error de validación: {e}[/red]")
        raise typer.Exit(1)
    
    except Exception as e:
        logger.exception("Error inesperado procesando CSV")
        console.print(f"[red]Error inesperado: {e}[/red]")
        raise typer.Exit(1)


@csv_to_md_router.command("validate")
def validate_csv_file(
    csv_file: Path = typer.Argument(..., help="Archivo CSV a validar")
) -> None:
    """
    Validar que un archivo CSV tenga las columnas requeridas.
    """
    try:
        processor = CSVToMarkdownProcessor(Path.cwd())  # El directorio no importa para validación
        columns = processor.validate_csv(csv_file)
        
        console.print(f"[green]✓ Archivo CSV válido[/green]")
        console.print(f"[blue]Archivo:[/blue] {csv_file}")
        console.print(f"[blue]Columnas encontradas:[/blue] {', '.join(sorted(columns))}")
        
        # Contar registros
        data = processor.read_csv_data(csv_file)
        console.print(f"[blue]Número de registros:[/blue] {len(data)}")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    
    except ValueError as e:
        console.print(f"[red]Error de validación: {e}[/red]")
        raise typer.Exit(1)
    
    except Exception as e:
        logger.exception("Error inesperado validando CSV")
        console.print(f"[red]Error inesperado: {e}[/red]")
        raise typer.Exit(1)