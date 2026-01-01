"""
Módulo para almacenar y buscar vectores usando ChromaDB
"""
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from config.settings import VECTORSTORE_DIR, TOP_K_RESULTS
from rich.console import Console

console = Console()


class VectorStore:
    """Gestiona el almacenamiento y búsqueda de vectores"""
    
    def __init__(self, collection_name: str = "documents", persist_directory: str = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or str(VECTORSTORE_DIR)
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa ChromaDB"""
        console.print("[yellow]Inicializando base de datos vectorial...[/yellow]")
        
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Obtener o crear colección SIN función de embedding por defecto
            # Usaremos sentence-transformers manualmente
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None  # Deshabilitar embedding por defecto
            )
            
            count = self.collection.count()
            console.print(f"[green]✓[/green] Base de datos lista ({count} documentos almacenados)")
            
        except Exception as e:
            console.print(f"[red]Error al inicializar ChromaDB:[/red] {e}")
            raise
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Agrega documentos a la base de datos
        
        Args:
            chunks: Lista de chunks con content y metadata
            embeddings: Lista de vectores de embedding
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Número de chunks y embeddings no coincide")
        
        console.print(f"[cyan]Almacenando {len(chunks)} chunks en la base de datos...[/cyan]")
        
        ids = [f"doc_{i}_{chunk['metadata'].get('chunk_id', i)}" for i, chunk in enumerate(chunks)]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            console.print(f"[green]✓[/green] {len(chunks)} chunks almacenados")
        except Exception as e:
            console.print(f"[red]Error al almacenar documentos:[/red] {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = TOP_K_RESULTS) -> List[Dict]:
        """
        Busca documentos similares
        
        Args:
            query_embedding: Vector de embedding de la consulta
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Formatear resultados
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            console.print(f"[red]Error en búsqueda:[/red] {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Retorna estadísticas de la colección"""
        return {
            'name': self.collection_name,
            'count': self.collection.count(),
            'persist_directory': self.persist_directory
        }
    
    def clear_collection(self):
        """Limpia la colección (cuidado: elimina todos los datos)"""
        console.print("[yellow]⚠ Limpiando colección...[/yellow]")
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None  # Deshabilitar embedding por defecto
            )
            console.print("[green]✓[/green] Colección limpiada")
        except Exception as e:
            console.print(f"[red]Error al limpiar colección:[/red] {e}")