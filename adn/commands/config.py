"""
Comando 'config' para gestionar la configuración de ADN CLI.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from ..utils import ConfigManager, get_logger

console = Console()
logger = get_logger(__name__)

# Sub-aplicación para comandos de configuración
config_router = typer.Typer(
    help="Comandos para gestionar la configuración",
    rich_markup_mode="rich"
)


@config_router.command("init")
def init_config(
    force: bool = typer.Option(False, "--force", "-f", help="Sobrescribir configuración existente")
) -> None:
    "Inicializar configuración de ADN CLI."
    
    config_manager = ConfigManager()
    
    try:
        config_file = config_manager.init_config(force=force)
        console.print(f"[green]Configuración inicializada en: {config_file}[/green]")
        
        # Mostrar configuración básica
        console.print("\n[bold]Configuración por defecto creada:[/bold]")
        show_config()
        
    except FileExistsError:
        console.print("[yellow]La configuración ya existe. Use --force para sobrescribir[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Error inicializando configuración")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("show")
def show_config() -> None:
    "Mostrar la configuración actual."
    
    config_manager = ConfigManager()
    
    try:
        config = config_manager.get_config()
        config_file = config_manager.config_file
        
        console.print(f"[bold]Configuración actual ({config_file}):[/bold]\n")
        
        # Crear tabla de configuración
        table = Table(title="Configuración ADN CLI")
        table.add_column("Parámetro", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green")
        table.add_column("Descripción", style="yellow")
        
        # Agregar filas de configuración
        table.add_row(
            "default_template",
            config.get("default_template", "default"),
            "Template por defecto para archivos de extracción"
        )
        table.add_row(
            "output_suffix",
            config.get("output_suffix", "_extraccion"),
            "Sufijo para archivos de salida"
        )
        table.add_row(
            "default_output_dir",
            str(config.get("default_output_dir", ".")),
            "Directorio de salida por defecto"
        )
        table.add_row(
            "log_level",
            config.get("log_level", "INFO"),
            "Nivel de logging"
        )
        table.add_row(
            "auto_open_generated",
            str(config.get("auto_open_generated", False)),
            "Abrir archivos generados automáticamente"
        )
        
        console.print(table)
        
        # Mostrar rutas importantes
        console.print(f"\n[bold]Rutas importantes:[/bold]")
        console.print(f"• Archivo de configuración: [cyan]{config_file}[/cyan]")
        console.print(f"• Directorio de templates: [cyan]{config_manager.templates_dir}[/cyan]")
        console.print(f"• Directorio de logs: [cyan]{config_manager.config_dir / 'logs'}[/cyan]")
        
    except FileNotFoundError:
        console.print("[yellow]Configuración no encontrada. Ejecute 'adn config init' para inicializar[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Error mostrando configuración")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("set")
def set_config(
    key: str = typer.Argument(..., help="Clave de configuración a modificar"),
    value: str = typer.Argument(..., help="Nuevo valor"),
) -> None:
    "Establecer un valor de configuración."
    
    config_manager = ConfigManager()
    
    try:
        # Validar clave de configuración
        valid_keys = [
            "default_template",
            "output_suffix", 
            "default_output_dir",
            "log_level",
            "auto_open_generated"
        ]
        
        if key not in valid_keys:
            console.print(f"[red]Clave no válida: {key}[/red]")
            console.print(f"Claves válidas: {', '.join(valid_keys)}")
            raise typer.Exit(1)
        
        # Convertir valor según el tipo esperado
        converted_value = _convert_config_value(key, value)
        
        # Actualizar configuración
        config_manager.set_config(key, converted_value)
        
        console.print(f"[green]Configuración actualizada: {key} = {converted_value}[/green]")
        
    except ValueError as e:
        console.print(f"[red]Valor no válido: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("Error estableciendo configuración")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("get")
def get_config(
    key: str = typer.Argument(..., help="Clave de configuración a obtener")
) -> None:
    "Obtener un valor de configuración."
    
    config_manager = ConfigManager()
    
    try:
        config = config_manager.get_config()
        
        if key in config:
            value = config[key]
            console.print(f"[cyan]{key}[/cyan]: [green]{value}[/green]")
        else:
            console.print(f"[red]Clave no encontrada: {key}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.exception("Error obteniendo configuración")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("template")
def edit_template(
    template_name: str = typer.Option("default", "--name", "-n", help="Nombre del template"),
    editor: Optional[str] = typer.Option(None, "--editor", "-e", help="Editor a usar"),
) -> None:
    "Editar o crear un template personalizado."
    
    config_manager = ConfigManager()
    
    try:
        template_file = config_manager.templates_dir / f"{template_name}.md"
        
        if not template_file.exists():
            # Crear template basado en el default
            from ..utils.template_engine import TemplateEngine
            template_engine = TemplateEngine()
            default_content = template_engine.get_template_content("default")
            
            template_file.write_text(default_content, encoding='utf-8')
            console.print(f"[green]Template creado: {template_file}[/green]")
        
        console.print(f"[blue]Template: {template_file}[/blue]")
        
        # Mostrar contenido actual
        content = template_file.read_text(encoding='utf-8')
        syntax = Syntax(content, "markdown", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        # Instrucciones para edición
        console.print(f"\n[yellow]Para editar este template:[/yellow]")
        if editor:
            console.print(f"  {editor} {template_file}")
        else:
            console.print(f"  code {template_file}  # VS Code")
            console.print(f"  nano {template_file}  # Editor de terminal")
            console.print(f"  notepad {template_file}  # Windows Notepad")
        
    except Exception as e:
        logger.exception("Error editando template")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("reset")
def reset_config(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirmar sin preguntar")
) -> None:
    "Restablecer configuración a valores por defecto."
    
    if not confirm:
        confirm_reset = typer.confirm("¿Está seguro de que desea restablecer la configuración?")
        if not confirm_reset:
            console.print("[yellow]Operación cancelada[/yellow]")
            return
    
    config_manager = ConfigManager()
    
    try:
        config_manager.reset_config()
        console.print("[green]Configuración restablecida a valores por defecto[/green]")
        
    except Exception as e:
        logger.exception("Error restableciendo configuración")
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_router.command("path")
def show_paths() -> None:
    "Mostrar rutas de archivos de configuración."
    
    config_manager = ConfigManager()
    
    console.print("[bold]Rutas de configuración ADN CLI:[/bold]\n")
    
    paths_table = Table()
    paths_table.add_column("Tipo", style="cyan")
    paths_table.add_column("Ruta", style="green")
    paths_table.add_column("Existe", style="yellow")
    
    paths_table.add_row(
        "Directorio base",
        str(config_manager.config_dir),
        "SI" if config_manager.config_dir.exists() else "NO"
    )
    paths_table.add_row(
        "Archivo de config",
        str(config_manager.config_file),
        "SI" if config_manager.config_file.exists() else "NO"
    )
    paths_table.add_row(
        "Directorio templates",
        str(config_manager.templates_dir),
        "SI" if config_manager.templates_dir.exists() else "NO"
    )
    
    logs_dir = config_manager.config_dir / "logs"
    paths_table.add_row(
        "Directorio logs",
        str(logs_dir),
        "SI" if logs_dir.exists() else "NO"
    )
    
    console.print(paths_table)


def _convert_config_value(key: str, value: str) -> any:
    "Convertir valor de configuración al tipo apropiado."
    
    boolean_keys = ["auto_open_generated"]
    
    if key in boolean_keys:
        if value.lower() in ["true", "1", "yes", "on"]:
            return True
        elif value.lower() in ["false", "0", "no", "off"]:
            return False
        else:
            raise ValueError(f"Valor booleano esperado para {key}: {value}")
    
    # Para otros tipos, mantener como string por ahora
    return value
