"""
Módulo para cargar diferentes tipos de documentos
"""
from pathlib import Path
from typing import List, Dict
import pypdf
from docx import Document
from rich.console import Console
from config.settings import SUPPORTED_EXTENSIONS

console = Console()


class DocumentLoader:
    """Carga documentos de diferentes formatos"""
    
    def __init__(self):
        self.supported_extensions = SUPPORTED_EXTENSIONS
    
    def load_document(self, file_path: str) -> Dict[str, any]:
        """
        Carga un documento y retorna su contenido
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Dict con 'content', 'metadata', 'file_type'
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension not in self.supported_extensions:
            raise ValueError(f"Formato no soportado: {extension}")
        
        console.print(f"[blue]Cargando:[/blue] {path.name}")
        
        if extension == '.txt':
            return self._load_txt(path)
        elif extension == '.pdf':
            return self._load_pdf(path)
        elif extension in ['.docx', '.doc']:
            return self._load_docx(path)
    
    def _load_txt(self, path: Path) -> Dict:
        """Carga archivo de texto plano"""
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'content': content,
            'metadata': {
                'source': str(path),
                'file_name': path.name,
                'file_type': 'text'
            },
            'file_type': 'text'
        }
    
    def _load_pdf(self, path: Path) -> Dict:
        """Carga archivo PDF"""
        content = []
        
        try:
            with open(path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        content.append(text)
            
            full_content = '\n\n'.join(content)
            
            return {
                'content': full_content,
                'metadata': {
                    'source': str(path),
                    'file_name': path.name,
                    'file_type': 'pdf',
                    'num_pages': num_pages
                },
                'file_type': 'pdf'
            }
        except Exception as e:
            console.print(f"[red]Error al leer PDF:[/red] {e}")
            raise
    
    def _load_docx(self, path: Path) -> Dict:
        """Carga archivo Word"""
        try:
            doc = Document(path)
            content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            
            full_content = '\n\n'.join(content)
            
            return {
                'content': full_content,
                'metadata': {
                    'source': str(path),
                    'file_name': path.name,
                    'file_type': 'docx',
                    'num_paragraphs': len(doc.paragraphs)
                },
                'file_type': 'docx'
            }
        except Exception as e:
            console.print(f"[red]Error al leer Word:[/red] {e}")
            raise
    
    def load_directory(self, directory_path: str) -> List[Dict]:
        """
        Carga todos los documentos soportados de un directorio
        
        Args:
            directory_path: Ruta al directorio
            
        Returns:
            Lista de documentos cargados
        """
        path = Path(directory_path)
        documents = []
        
        if not path.is_dir():
            raise ValueError(f"No es un directorio válido: {directory_path}")
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    doc = self.load_document(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    console.print(f"[yellow]Advertencia:[/yellow] No se pudo cargar {file_path.name}: {e}")
        
        console.print(f"[green]✓[/green] Cargados {len(documents)} documentos")
        return documents