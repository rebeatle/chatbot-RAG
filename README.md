# Chatbot RAG Local con DeepSeek-R1

Sistema de recuperación y generación aumentada (RAG) completamente local usando DeepSeek-R1 via Ollama.

## Características

- ✅ 100% Local (sin APIs externas)
- 📄 Soporta PDF, Word (.docx), TXT
- 🧠 Embeddings de alta calidad (all-mpnet-base-v2)
- 💾 Base de datos vectorial persistente (ChromaDB)
- 🚀 Interfaz CLI intuitiva

## Requisitos

- Python 3.10+
- Ollama instalado con modelo `deepseek-r1:1.5b`

## Instalación

1. **Clonar repositorio**
```bash
git clone <tu-repo>
cd chatbot-rag
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar .env**
```bash
# El archivo .env ya está configurado por defecto
# Ajusta los valores si es necesario
```

5. **Crear directorios necesarios**
```bash
mkdir -p data/documents data/vectorstore
```

## Uso

### 1. Iniciar el sistema
```bash
python main.py
```

### 2. Indexar documentos
Coloca tus documentos (PDF, DOCX, TXT) en `data/documents/` y ejecuta:
```
/index
```

O especifica un directorio:
```
/index /ruta/a/tus/documentos
```

### 3. Hacer preguntas
Simplemente escribe tu pregunta:
```
¿Qué dice el documento sobre...?
```

### 4. Comandos disponibles
- `/index [ruta]` - Indexar documentos
- `/stats` - Ver estadísticas
- `/clear` - Limpiar índice
- `/help` - Mostrar ayuda
- `/exit` - Salir

## Estructura del Proyecto
```
chatbot-rag/
├── config/
│   └── settings.py          # Configuración centralizada
├── src/
│   ├── document_loader.py   # Carga de documentos
│   ├── text_processor.py    # División en chunks
│   ├── embeddings.py        # Generación de embeddings
│   ├── vector_store.py      # ChromaDB
│   ├── llm_client.py        # Cliente Ollama
│   └── rag_engine.py        # Motor principal
├── utils/
│   └── helpers.py           # Utilidades
├── data/
│   ├── documents/           # Tus documentos aquí
│   └── vectorstore/         # Base de datos (auto-generado)
└── main.py                  # CLI principal
```

## Configuración

Edita `.env` para ajustar:
- Tamaño de chunks
- Número de resultados
- Temperatura del modelo
- Rutas personalizadas

## Troubleshooting

**Error: Modelo no encontrado**
```bash
ollama pull deepseek-r1:1.5b
```

**Error: Ollama no responde**
```bash
# Asegúrate de que Ollama esté corriendo
ollama serve
```

**Embeddings muy lentos**
- Primera vez: Descarga ~420MB (normal)
- Después: Debería ser rápido



## Licencia

Uso personal y educativo