"""
Funciones auxiliares
"""
from pathlib import Path
from typing import List
from rich.table import Table
from rich.console import Console

console = Console()


def print_welcome():
    """Imprime mensaje de bienvenida"""
    console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   CHATBOT RAG LOCAL - DeepSeek-R1   ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")


def print_help():
    """Imprime ayuda de comandos"""
    table = Table(title="Comandos Disponibles", show_header=True)
    table.add_column("Comando", style="cyan", no_wrap=True)
    table.add_column("Descripción", style="white")
    
    table.add_row("/index [ruta]", "Indexar documentos de un directorio")
    table.add_row("/stats", "Ver estadísticas del sistema")
    table.add_row("/clear", "Limpiar índice de documentos")
    table.add_row("/help", "Mostrar esta ayuda")
    table.add_row("/exit", "Salir del programa")
    table.add_row("[pregunta]", "Hacer una pregunta al sistema")
    
    console.print(table)
    console.print()


def print_sources(sources: List[dict]):
    """Imprime fuentes de información"""
    if not sources:
        return
    
    console.print("\n[bold]Fuentes:[/bold]")
    for i, source in enumerate(sources, 1):
        relevance = source.get('relevance')
        relevance_str = f" ({relevance:.2%} relevante)" if relevance else ""
        console.print(f"  {i}. {source['file']}{relevance_str}")


def validate_directory(path: str) -> bool:
    """Valida que sea un directorio válido"""
    p = Path(path)
    return p.exists() and p.is_dir()


def format_answer(answer: str) -> str:
    """Formatea la respuesta para mejor visualización"""
    return answer.strip()