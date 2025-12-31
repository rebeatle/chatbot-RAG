"""
Módulo para procesar y dividir texto en chunks
"""
from typing import List, Dict
import tiktoken
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from rich.console import Console

console = Console()


class TextProcessor:
    """Procesa y divide texto en fragmentos manejables"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Cuenta tokens en un texto"""
        return len(self.encoding.encode(text))
    
    def split_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Divide texto en chunks con overlap
        
        Args:
            text: Texto a dividir
            metadata: Metadatos del documento
            
        Returns:
            Lista de chunks con metadata
        """
        if not text or not text.strip():
            return []
        
        # Dividir por párrafos primero
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            # Si un párrafo es muy grande, dividirlo por oraciones
            if para_tokens > self.chunk_size:
                # Si hay contenido en current_chunk, guardarlo primero
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata, len(chunks)))
                    current_chunk = []
                    current_length = 0
                
                # Dividir párrafo grande
                sentences = para.split('. ')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sent_tokens = self.count_tokens(sentence)
                    
                    if current_length + sent_tokens > self.chunk_size and current_chunk:
                        chunks.append(self._create_chunk(current_chunk, metadata, len(chunks)))
                        # Mantener overlap
                        overlap_text = ' '.join(current_chunk[-2:]) if len(current_chunk) >= 2 else ''
                        current_chunk = [overlap_text] if overlap_text else []
                        current_length = self.count_tokens(overlap_text) if overlap_text else 0
                    
                    current_chunk.append(sentence)
                    current_length += sent_tokens
            else:
                # Párrafo normal
                if current_length + para_tokens > self.chunk_size and current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata, len(chunks)))
                    # Mantener overlap
                    overlap_text = ' '.join(current_chunk[-1:])
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = self.count_tokens(overlap_text) if overlap_text else 0
                
                current_chunk.append(para)
                current_length += para_tokens
        
        # Agregar último chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, metadata, len(chunks)))
        
        console.print(f"[cyan]→[/cyan] Texto dividido en {len(chunks)} chunks")
        return chunks
    
    def _create_chunk(self, text_parts: List[str], metadata: Dict, chunk_id: int) -> Dict:
        """Crea un chunk con metadata"""
        content = '\n\n'.join(text_parts)
        
        chunk_metadata = metadata.copy() if metadata else {}
        chunk_metadata['chunk_id'] = chunk_id
        chunk_metadata['tokens'] = self.count_tokens(content)
        
        return {
            'content': content,
            'metadata': chunk_metadata
        }
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Procesa múltiples documentos
        
        Args:
            documents: Lista de documentos cargados
            
        Returns:
            Lista de todos los chunks
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.split_text(doc['content'], doc['metadata'])
            all_chunks.extend(chunks)
        
        console.print(f"[green]✓[/green] Total de chunks generados: {len(all_chunks)}")
        return all_chunks