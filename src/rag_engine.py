"""
Motor principal del sistema RAG
"""
from typing import List, Dict
from src.document_loader import DocumentLoader
from src.text_processor import TextProcessor
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.llm_client import LLMClient
from rich.console import Console

console = Console()


class RAGEngine:
    """Motor principal que coordina todos los componentes del RAG"""
    
    def __init__(self):
        console.print("[bold cyan]Inicializando RAG Engine...[/bold cyan]")
        
        self.document_loader = DocumentLoader()
        self.text_processor = TextProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()
        
        console.print("[bold green]✓ RAG Engine listo[/bold green]\n")
    
    def index_documents(self, directory_path: str):
        """
        Indexa todos los documentos de un directorio
        
        Args:
            directory_path: Ruta al directorio con documentos
        """
        console.print(f"[bold]Iniciando indexación de documentos...[/bold]\n")
        
        # 1. Cargar documentos
        documents = self.document_loader.load_directory(directory_path)
        
        if not documents:
            console.print("[yellow]⚠ No se encontraron documentos para indexar[/yellow]")
            return
        
        # 2. Procesar y dividir en chunks
        chunks = self.text_processor.process_documents(documents)
        
        # 3. Generar embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        # 4. Almacenar en base de datos vectorial
        self.vector_store.add_documents(chunks, embeddings)
        
        console.print(f"\n[bold green]✓ Indexación completada exitosamente[/bold green]")
    
    def query(self, question: str, top_k: int = 3) -> Dict:
        """
        Realiza una consulta al sistema RAG
        
        Args:
            question: Pregunta del usuario
            top_k: Número de documentos relevantes a recuperar
            
        Returns:
            Dict con 'answer' y 'sources'
        """
        # 1. Generar embedding de la pregunta
        question_embedding = self.embedding_generator.generate_embedding(question)
        
        # 2. Buscar documentos relevantes
        relevant_docs = self.vector_store.search(question_embedding, top_k)
        
        if not relevant_docs:
            return {
                'answer': "No encontré información relevante en los documentos indexados.",
                'sources': []
            }
        
        # 3. Generar respuesta con LLM
        answer = self.llm_client.generate_with_context(question, relevant_docs)
        
        # 4. Extraer fuentes
        sources = []
        for doc in relevant_docs:
            source_info = {
                'file': doc['metadata'].get('file_name', 'Desconocido'),
                'chunk_id': doc['metadata'].get('chunk_id', 0),
                'relevance': 1 - doc['distance'] if doc['distance'] else None
            }
            sources.append(source_info)
        
        return {
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources)
        }
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del sistema"""
        return {
            'vectorstore': self.vector_store.get_collection_stats(),
            'embedding_dim': self.embedding_generator.get_embedding_dimension(),
            'model': self.llm_client.model
        }
    
    def clear_index(self):
        """Limpia el índice de documentos"""
        self.vector_store.clear_collection()