"""
Configuración de la aplicación RAG.
Este módulo carga las variables de entorno necesarias para la aplicación.
"""

import os
from dotenv import load_dotenv

# Variables globales
OPENAI_API_KEY = None
SUPABASE_URL = None
SUPABASE_KEY = None
SUPABASE_COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

def load_environment_variables():
    """Carga las variables de entorno desde .env o desde Vercel."""
    global OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY, SUPABASE_COLLECTION_NAME
    global EMBEDDING_MODEL, LLM_MODEL
    
    # Intentar cargar desde .env si estamos en desarrollo
    try:
        from pathlib import Path
        dotenv_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(dotenv_path)
    except:
        pass
    
    # Cargar variables (Vercel las proporciona automáticamente como variables de entorno)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_COLLECTION_NAME = os.getenv("SUPABASE_COLLECTION_NAME", SUPABASE_COLLECTION_NAME)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)
    LLM_MODEL = os.getenv("LLM_MODEL", LLM_MODEL)

# Cargar variables de entorno al importar el módulo
load_environment_variables() 