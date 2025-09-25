"""
Comando 'create' para generar archivos de extracción de PDFs.
"""

import glob
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils import FileHandler, TemplateEngine, get_logger, validate_pdf_file

console = Console()
logger = get_logger(__name__)

# Sub-aplicación para comandos 'gen-md-from-pdf'
create_router = typer.Typer(
    help="Genera archivos Markdown a partir de PDFs para extracción de información",
    rich_markup_mode="rich"
)


@create_router.command("file")
def create_file(
    pdf_file: Path = typer.Argument(..., help="Archivo PDF a procesar"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida para archivos generados"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template personalizado a usar"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Sobrescribir archivo existente"
    ),
) -> None:
    """Generar archivo Markdown de extracción para un PDF específico."""
    
    # Validar archivo PDF
    if not validate_pdf_file(pdf_file):
        console.print(f"[red]Error: {pdf_file} no es un archivo PDF válido[/red]")
        raise typer.Exit(1)
    
    # Configurar directorio de salida
    output_directory = output_dir or pdf_file.parent
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Generar archivo de extracción
    file_handler = FileHandler()
    template_engine = TemplateEngine()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Procesando {pdf_file.name}...", total=None)
            
            # Generar el archivo Markdown
            output_file = file_handler.generate_extraction_file(
                pdf_file=pdf_file,
                output_dir=output_directory,
                template_name=template,
                force=force
            )
            
            progress.update(task, completed=True)
        
        console.print(f"[green]Archivo creado: {output_file}[/green]")
        
    except FileExistsError:
        console.print(f"[yellow]El archivo ya existe. Use --force para sobrescribir[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception(f"Error procesando {pdf_file}")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@create_router.command("all")
def create_all(
    directory: Optional[Path] = typer.Argument(
        None, help="Directorio a procesar (por defecto: directorio actual)"
    ),
    pattern: str = typer.Option("*.pdf", "--pattern", "-p", help="Patrón de archivos PDF"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template personalizado"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Sobrescribir archivos existentes"),
    skip_processed: bool = typer.Option(
        True, "--skip-processed", help="Omitir archivos ya procesados"
    ),
) -> None:
    """Generar archivos Markdown de extracción para todos los PDFs en un directorio."""
    
    target_dir = directory or Path.cwd()
    
    if not target_dir.exists():
        console.print(f"[red]Error: El directorio {target_dir} no existe[/red]")
        raise typer.Exit(1)
    
    # Buscar archivos PDF
    file_handler = FileHandler()
    pdf_files = file_handler.find_pdf_files(target_dir, pattern)
    
    if not pdf_files:
        console.print(f"[yellow]No se encontraron archivos PDF en {target_dir}[/yellow]")
        return
    
    # Filtrar archivos ya procesados si es necesario
    if skip_processed and not force:
        pdf_files = [f for f in pdf_files if not file_handler.is_processed(f)]
        if not pdf_files:
            console.print("[green]Todos los archivos ya han sido procesados[/green]")
            return
    
    console.print(f"[blue]Procesando {len(pdf_files)} archivos PDF...[/blue]")
    
    # Configurar directorio de salida
    output_directory = output_dir or target_dir
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Procesar archivos
    success_count = 0
    error_count = 0
    
    with Progress(console=console) as progress:
        task = progress.add_task("Procesando archivos...", total=len(pdf_files))
        
        for pdf_file in pdf_files:
            try:
                progress.update(task, description=f"Procesando {pdf_file.name}")
                
                output_file = file_handler.generate_extraction_file(
                    pdf_file=pdf_file,
                    output_dir=output_directory,
                    template_name=template,
                    force=force
                )
                
                success_count += 1
                logger.info(f"Procesado: {pdf_file} -> {output_file}")
                
            except FileExistsError:
                logger.warning(f"Ya existe: {pdf_file}")
                continue
            except Exception as e:
                error_count += 1
                logger.error(f"Error procesando {pdf_file}: {e}")
                continue
            finally:
                progress.advance(task)
    
    # Mostrar resumen
    console.print("\n[bold]Resumen:[/bold]")
    console.print(f"Procesados exitosamente: {success_count}")
    if error_count > 0:
        console.print(f"Errores: {error_count}")
    
    if error_count > 0:
        console.print("\n[yellow]Revise los logs para detalles de errores[/yellow]")


@create_router.command("glob")
def create_glob(
    pattern: str = typer.Argument(..., help="Patrón glob para archivos PDF"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template personalizado"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Sobrescribir archivos existentes"),
) -> None:
    """Generar archivos Markdown de extracción usando patrones glob."""
    
    # Buscar archivos usando glob
    pdf_files = [Path(f) for f in glob.glob(pattern) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        console.print(f"[yellow]No se encontraron archivos PDF con el patrón: {pattern}[/yellow]")
        return
    
    console.print(f"[blue]Encontrados {len(pdf_files)} archivos PDF[/blue]")
    
    # Configurar directorio de salida
    output_directory = output_dir or Path.cwd()
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Procesar archivos
    file_handler = FileHandler()
    success_count = 0
    
    with Progress(console=console) as progress:
        task = progress.add_task("Procesando archivos...", total=len(pdf_files))
        
        for pdf_file in pdf_files:
            try:
                progress.update(task, description=f"Procesando {pdf_file.name}")
                
                if not validate_pdf_file(pdf_file):
                    logger.warning(f"Archivo no válido: {pdf_file}")
                    continue
                
                output_file = file_handler.generate_extraction_file(
                    pdf_file=pdf_file,
                    output_dir=output_directory,
                    template_name=template,
                    force=force
                )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error procesando {pdf_file}: {e}")
            finally:
                progress.advance(task)
    
    console.print(f"\n[green]Procesados {success_count} de {len(pdf_files)} archivos[/green]")


# Comando por defecto (alias para create_file)
@create_router.callback(invoke_without_command=True)
def create_default(
    ctx: typer.Context,
    files: Optional[List[str]] = typer.Argument(None, help="Archivos PDF a procesar"),
    all_flag: bool = typer.Option(False, "--all", help="Procesar todos los PDFs del directorio"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template personalizado"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Sobrescribir archivos existentes"),
) -> None:
    """
    Generar archivos Markdown de extracción para PDFs.
    
    Si no se especifica ningún comando, se comporta como 'gen-md-from-pdf file' o 'gen-md-from-pdf all'.
    """
    
    # Si se invocó un subcomando, no hacer nada
    if ctx.invoked_subcommand is not None:
        return
    
    # Procesar todos los archivos si se especifica --all
    if all_flag:
        ctx.invoke(create_all, 
                  directory=None,
                  pattern="*.pdf",
                  output_dir=output_dir, 
                  template=template, 
                  force=force,
                  skip_processed=True)
        return
    
    # Si no se proporcionan archivos, mostrar ayuda
    if not files:
        console.print(ctx.get_help())
        return
    
    # Procesar archivos individuales
    for file_path in files:
        pdf_file = Path(file_path)
        ctx.invoke(create_file,
                  pdf_file=pdf_file,
                  output_dir=output_dir,
                  template=template,
                  force=force)