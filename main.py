"""
Punto de entrada principal del chatbot RAG
"""
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from src.rag_engine import RAGEngine
from utils.helpers import (
    print_welcome,
    print_help,
    print_sources,
    validate_directory,
    format_answer
)
from config.settings import DOCUMENTS_DIR

console = Console()


def main():
    """Función principal del CLI"""
    print_welcome()
    
    try:
        # Inicializar RAG Engine
        rag = RAGEngine()
        
        # Mensaje inicial
        console.print("[green]Sistema listo. Escribe /help para ver comandos disponibles.[/green]\n")
        
        # Loop principal
        while True:
            try:
                # Obtener input del usuario
                user_input = Prompt.ask("\n[bold cyan]Tú[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                # Procesar comandos
                if user_input.startswith('/'):
                    handle_command(user_input, rag)
                else:
                    # Es una pregunta
                    handle_query(user_input, rag)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Usa /exit para salir[/yellow]")
                continue
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
    
    except Exception as e:
        console.print(f"\n[bold red]Error fatal:[/bold red] {e}")
        console.print("[yellow]Asegúrate de que Ollama esté corriendo: ollama serve[/yellow]")
        sys.exit(1)


def handle_command(command: str, rag: RAGEngine):
    """Maneja comandos del sistema"""
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None
    
    if cmd == '/help':
        print_help()
    
    elif cmd == '/exit' or cmd == '/quit':
        console.print("\n[cyan]¡Hasta luego![/cyan]\n")
        sys.exit(0)
    
    elif cmd == '/index':
        if not arg:
            # Usar directorio por defecto
            arg = str(DOCUMENTS_DIR)
            console.print(f"[yellow]Usando directorio por defecto:[/yellow] {arg}")
        
        if not validate_directory(arg):
            console.print(f"[red]Error:[/red] '{arg}' no es un directorio válido")
            return
        
        try:
            rag.index_documents(arg)
        except Exception as e:
            console.print(f"[red]Error al indexar:[/red] {e}")
    
    elif cmd == '/stats':
        stats = rag.get_stats()
        
        panel_content = f"""[cyan]Documentos indexados:[/cyan] {stats['vectorstore']['count']}
[cyan]Dimensión de embeddings:[/cyan] {stats['embedding_dim']}
[cyan]Modelo LLM:[/cyan] {stats['model']}
[cyan]Directorio vectorstore:[/cyan] {stats['vectorstore']['persist_directory']}"""
        
        console.print(Panel(panel_content, title="Estadísticas del Sistema", border_style="green"))
    
    elif cmd == '/clear':
        confirm = Prompt.ask(
            "[yellow]¿Estás seguro de que quieres limpiar el índice?[/yellow] (sí/no)",
            default="no"
        )
        if confirm.lower() in ['sí', 'si', 'yes', 's', 'y']:
            rag.clear_index()
        else:
            console.print("[cyan]Operación cancelada[/cyan]")
    
    else:
        console.print(f"[red]Comando desconocido:[/red] {cmd}")
        console.print("[yellow]Escribe /help para ver comandos disponibles[/yellow]")


def handle_query(question: str, rag: RAGEngine):
    """Maneja una pregunta del usuario"""
    console.print("\n[yellow]Buscando información...[/yellow]")
    
    try:
        result = rag.query(question)
        
        # Mostrar respuesta
        answer = format_answer(result['answer'])
        console.print(f"\n[bold green]Respuesta:[/bold green]\n")
        console.print(Panel(answer, border_style="green"))
        
        # Mostrar fuentes
        if result['sources']:
            print_sources(result['sources'])
    
    except Exception as e:
        console.print(f"[red]Error al procesar pregunta:[/red] {e}")


if __name__ == "__main__":
    main()