# RAGLEC Web - Interfaz web para el sistema RAG

Esta es una versión adaptada del sistema RAGLEC para funcionar en Vercel, proporcionando una interfaz web para realizar consultas a la base de datos vectorial.

## Estructura del proyecto

```
raglec-vercel/
├── api/                   # Funciones serverless de Python para Vercel
│   ├── query.py           # Endpoint para consultas RAG
│   └── requirements.txt   # Dependencias Python
├── app/                   # Código principal de la aplicación
│   ├── config/            # Configuración
│   ├── database/          # Conexión a Supabase
│   ├── document_processing/# Procesamiento de documentos
│   ├── query/             # Motor de consultas RAG
│   └── utils/             # Utilidades
├── public/                # Archivos estáticos
│   ├── css/               # Estilos CSS
│   └── js/                # JavaScript
├── pages/                 # Páginas del frontend
│   └── index.html         # Página principal
└── vercel.json            # Configuración de Vercel
```

## Requisitos

Este proyecto requiere:

- Una cuenta de Vercel
- Una base de datos Supabase configurada con la extensión pgvector
- Una cuenta de OpenAI con acceso a la API

## Despliegue

### 1. Configurar Supabase

Asegúrate de tener configurada una base de datos Supabase con:
- La extensión pgvector habilitada
- Una tabla `documents` con la estructura adecuada para almacenar embeddings
- La función SQL `match_documents` para búsqueda por similitud

### 2. Configurar variables de entorno en Vercel

Configura las siguientes variables de entorno en tu proyecto Vercel:

- `OPENAI_API_KEY`: Tu clave de API de OpenAI
- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_KEY`: Clave de API de Supabase
- `SUPABASE_COLLECTION_NAME`: Nombre de la colección (por defecto "documents")
- `EMBEDDING_MODEL`: Modelo de embeddings a utilizar (por defecto "text-embedding-3-small")
- `LLM_MODEL`: Modelo de lenguaje a utilizar (por defecto "gpt-4o-mini")

### 3. Desplegar en Vercel

```bash
vercel login
vercel
```

Para producción:

```bash
vercel --prod
```

## Desarrollo local

1. Clona este repositorio
2. Crea un archivo `.env` con las variables de entorno necesarias (ver `.env.example`)
3. Instala las dependencias:
   ```bash
   pip install -r api/requirements.txt
   ```
4. Ejecuta el servidor de desarrollo de Vercel:
   ```bash
   vercel dev
   ```

## Limitaciones

- La versión web de RAGLEC solo proporciona la funcionalidad de consulta.
- El monitoreo de Google Drive y el procesamiento de documentos no están incluidos en esta versión.
- El tiempo máximo de ejecución está limitado por Vercel (10s en plan gratuito, 60s en planes pagos).

## Relacionado

Este proyecto es una adaptación del sistema RAGLEC original para funcionar como una aplicación web en Vercel. 