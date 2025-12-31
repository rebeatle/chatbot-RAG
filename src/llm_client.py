"""
Módulo para comunicación con Ollama
"""
import ollama
from typing import List, Dict
from config.settings import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE, MAX_TOKENS
from rich.console import Console

console = Console()


class LLMClient:
    """Cliente para interactuar con modelos LLM locales via Ollama"""
    
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
        self._verify_model()
    
    def _verify_model(self):
        """Verifica que el modelo esté disponible"""
        try:
            models = self.client.list()
            model_names = [m['name'] for m in models['models']]
            
            if self.model not in model_names:
                console.print(f"[red]⚠ Modelo '{self.model}' no encontrado[/red]")
                console.print(f"[yellow]Modelos disponibles:[/yellow] {', '.join(model_names)}")
                raise ValueError(f"Modelo {self.model} no disponible")
            
            console.print(f"[green]✓[/green] Modelo {self.model} disponible")
        except Exception as e:
            console.print(f"[red]Error al verificar modelo:[/red] {e}")
            console.print("[yellow]Asegúrate de que Ollama esté corriendo: ollama serve[/yellow]")
            raise
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = TEMPERATURE) -> str:
        """
        Genera respuesta del modelo
        
        Args:
            prompt: Texto de entrada
            system_prompt: Instrucciones del sistema (opcional)
            temperature: Temperatura para generación
            
        Returns:
            Respuesta generada
        """
        messages = []
        
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    'temperature': temperature,
                    'num_predict': MAX_TOKENS
                }
            )
            
            return response['message']['content']
        except Exception as e:
            console.print(f"[red]Error al generar respuesta:[/red] {e}")
            raise
    
    def generate_with_context(self, query: str, context_docs: List[Dict], temperature: float = TEMPERATURE) -> str:
        """
        Genera respuesta usando documentos de contexto
        
        Args:
            query: Pregunta del usuario
            context_docs: Documentos relevantes
            temperature: Temperatura para generación
            
        Returns:
            Respuesta generada
        """
        # Construir contexto
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            source = doc['metadata'].get('file_name', 'Desconocido')
            content = doc['content']
            context_parts.append(f"[Documento {i} - {source}]\n{content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # System prompt para RAG
        system_prompt = """Eres un asistente útil que responde preguntas basándose en documentos proporcionados.

INSTRUCCIONES:
1. Responde SOLO basándote en la información de los documentos proporcionados
2. Si la información no está en los documentos, di claramente que no tienes esa información
3. Cita las fuentes cuando sea posible mencionando el número del documento
4. Sé conciso pero completo en tus respuestas
5. Si hay información contradictoria, menciona ambas versiones"""
        
        # Construir prompt
        prompt = f"""Contexto de documentos:

{context}

---

Pregunta del usuario: {query}

Respuesta basada en los documentos:"""
        
        return self.generate(prompt, system_prompt, temperature)