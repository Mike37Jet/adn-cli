#!/usr/bin/env python3
"""
CLI principal para ADN - Automatización de Documentos y Notas

Este módulo define la interfaz de línea de comandos principal usando Typer.
"""

import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .commands import config_router, create_router, csv_to_md_router
from .utils import get_logger, setup_logging

# Configuración global
console = Console()
logger = get_logger(__name__)

# Aplicación principal de Typer
app = typer.Typer(
    name="adn",
    help="ADN CLI - Automatización de Documentos y Notas",
    add_completion=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Agregar sub-comandos
app.add_typer(create_router, name="gen-md-from-pdf", help="Genera un archivo Markdown a partir de un PDF para extracción de información")
app.add_typer(config_router, name="config", help="Gestionar configuración")
app.add_typer(csv_to_md_router, name="csv-to-md", help="Convertir CSV a archivos Markdown")


@app.command()
def list_files(
    directory: Optional[Path] = typer.Argument(
        None,
        help="Directorio a escanear (por defecto: directorio actual)"
    ),
    pattern: str = typer.Option("*.pdf", "--pattern", "-p", help="Patrón de archivos"),
    show_processed: bool = typer.Option(False, "--processed", help="Mostrar archivos ya procesados"),
) -> None:
    """Listar archivos PDF en el directorio especificado."""
    from .utils.file_handler import FileHandler
    
    setup_logging()
    
    target_dir = directory or Path.cwd()
    
    if not target_dir.exists():
        console.print(f"[red]Error: El directorio {target_dir} no existe[/red]")
        raise typer.Exit(1)
    
    file_handler = FileHandler()
    pdf_files = file_handler.find_pdf_files(target_dir, pattern)
    
    if not pdf_files:
        console.print(f"[yellow]No se encontraron archivos PDF en {target_dir}[/yellow]")
        return
    
    # Crear tabla para mostrar archivos
    table = Table(title=f"Archivos PDF en {target_dir}")
    table.add_column("Archivo", style="cyan")
    table.add_column("Tamaño", style="green")
    table.add_column("Estado", style="yellow")
    
    for pdf_file in sorted(pdf_files):
        size = file_handler.get_file_size(pdf_file)
        status = "Procesado" if file_handler.is_processed(pdf_file) else "Pendiente"
        
        if not show_processed and status == "Procesado":
            continue
            
        table.add_row(pdf_file.name, size, status)
    
    console.print(table)


@app.command()
def status(
    directory: Optional[Path] = typer.Argument(
        None,
        help="Directorio a verificar (por defecto: directorio actual)"
    )
) -> None:
    """Mostrar el estado de procesamiento de archivos."""
    from .utils.file_handler import FileHandler
    
    setup_logging()
    
    target_dir = directory or Path.cwd()
    file_handler = FileHandler()
    
    pdf_files = file_handler.find_pdf_files(target_dir)
    processed_files = [f for f in pdf_files if file_handler.is_processed(f)]
    pending_files = [f for f in pdf_files if not file_handler.is_processed(f)]
    
    console.print(f"[bold]Estado del directorio: {target_dir}[/bold]")
    console.print(f"Total de PDFs: {len(pdf_files)}")
    console.print(f"Procesados: {len(processed_files)}")
    console.print(f"Pendientes: {len(pending_files)}")
    
    if pending_files:
        console.print("\n[yellow]Archivos pendientes:[/yellow]")
        for file in pending_files[:5]:  # Mostrar solo los primeros 5
            console.print(f"  • {file.name}")
        if len(pending_files) > 5:
            console.print(f"  ... y {len(pending_files) - 5} más")


@app.command()
def clean(
    directory: Optional[Path] = typer.Argument(
        None,
        help="Directorio a limpiar (por defecto: directorio actual)"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo mostrar qué se eliminaría"),
    force: bool = typer.Option(False, "--force", "-f", help="No pedir confirmación"),
) -> None:
    """Limpiar archivos temporales y caches."""
    from .utils.file_handler import FileHandler
    
    setup_logging()
    
    target_dir = directory or Path.cwd()
    file_handler = FileHandler()
    
    # Buscar archivos temporales
    temp_patterns = ["*.tmp", "*.temp", "*~", ".adn_cache/*"]
    temp_files = []
    
    for pattern in temp_patterns:
        temp_files.extend(target_dir.glob(pattern))
    
    if not temp_files:
        console.print("[green]No se encontraron archivos temporales para limpiar[/green]")
        return
    
    console.print(f"[yellow]Se encontraron {len(temp_files)} archivos temporales:[/yellow]")
    for file in temp_files:
        console.print(f"  • {file.name}")
    
    if dry_run:
        console.print("\n[blue]Modo dry-run: No se eliminaron archivos[/blue]")
        return
    
    if not force:
        confirm = typer.confirm("¿Desea eliminar estos archivos?")
        if not confirm:
            console.print("[yellow]Operación cancelada[/yellow]")
            return
    
    # Eliminar archivos
    deleted_count = 0
    for file in temp_files:
        try:
            file.unlink()
            deleted_count += 1
            logger.debug(f"Eliminado: {file}")
        except Exception as e:
            console.print(f"[red]Error al eliminar {file}: {e}[/red]")
    
    console.print(f"[green]Se eliminaron {deleted_count} archivos temporales[/green]")


def version_callback(value: bool):
    """Callback para manejar la opción de versión."""
    if value:
        console.print(__version__)
        raise typer.Exit()

@app.callback()
def main(
    version_flag: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Mostrar versión y salir", callback=version_callback
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Activar logging detallado"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suprimir salida no esencial"),
) -> None:
    """
    ADN CLI - Automatización de Documentos y Notas
    
    Framework CLI profesional para automatizar la creación de documentos de 
    extracción y notas estructuradas a partir de archivos PDF y conversión
    de archivos CSV a documentos Markdown.
    
    Ejemplos de uso:
    
        # Generar archivo Markdown para un PDF
        adn gen-md-from-pdf documento.pdf
        
        # Generar archivo en directorio específico
        adn gen-md-from-pdf documento.pdf --output-dir /ruta/destino
        
        # Procesar todos los PDFs del directorio
        adn gen-md-from-pdf --all
        
        # Procesar todos los PDFs y guardar en directorio específico
        adn gen-md-from-pdf --all --output-dir /ruta/destino
        
        # Convertir CSV a archivos Markdown
        adn csv-to-md convert datos.csv
        
        # Convertir CSV y guardar en directorio específico
        adn csv-to-md convert datos.csv --output-dir /ruta/destino
        
        # Validar archivo CSV antes de procesar
        adn csv-to-md validate datos.csv
        
        # Configurar ADN CLI
        adn config --init
        
        # Ver estado de archivos
        adn status
    """
    
    # Configurar logging según las opciones
    if verbose:
        setup_logging(level="DEBUG")
    elif quiet:
        setup_logging(level="WARNING")
    else:
        setup_logging(level="INFO")


def cli() -> None:
    """Punto de entrada para el CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operación interrumpida por el usuario[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Error inesperado en CLI")
        console.print(f"[red]Error inesperado: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    cli()