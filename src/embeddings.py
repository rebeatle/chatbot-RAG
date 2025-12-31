"""
Módulo para generar embeddings usando sentence-transformers
"""
from typing import List
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class EmbeddingGenerator:
    """Genera embeddings usando modelos locales"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo de embeddings (descarga si es necesario)"""
        console.print(f"[yellow]Cargando modelo de embeddings:[/yellow] {self.model_name}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Descargando/Cargando modelo...", total=None)
            
            try:
                self.model = SentenceTransformer(self.model_name)
                progress.update(task, completed=True)
                console.print("[green]✓[/green] Modelo cargado exitosamente")
            except Exception as e:
                console.print(f"[red]Error al cargar modelo:[/red] {e}")
                raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Vector de embedding
        """
        if not self.model:
            raise RuntimeError("Modelo no cargado")
        
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Genera embeddings para múltiples textos
        
        Args:
            texts: Lista de textos
            show_progress: Mostrar barra de progreso
            
        Returns:
            Lista de vectores de embedding
        """
        if not self.model:
            raise RuntimeError("Modelo no cargado")
        
        if show_progress:
            console.print(f"[cyan]Generando embeddings para {len(texts)} textos...[/cyan]")
        
        embeddings = self.model.encode(
            texts,
            convert_to_tensor=False,
            show_progress_bar=show_progress
        )
        
        if show_progress:
            console.print("[green]✓[/green] Embeddings generados")
        
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """Retorna la dimensión del embedding"""
        return self.model.get_sentence_embedding_dimension()