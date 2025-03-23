"""
Generación de embeddings para documentos.
"""

import logging
import traceback
from typing import List, Union

from openai import OpenAI
from app.config.settings import OPENAI_API_KEY, EMBEDDING_MODEL

# Configurar logging
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Clase para generar embeddings de documentos."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, api_key: str = OPENAI_API_KEY):
        """Inicializa el generador de embeddings.
        
        Args:
            model_name: Nombre del modelo de embeddings.
            api_key: Clave API de OpenAI.
        """
        if not api_key:
            logger.error("No se ha proporcionado la clave API de OpenAI")
            raise ValueError("No se ha proporcionado la clave API de OpenAI para el generador de embeddings")
            
        self.model_name = model_name
        
        try:
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Generador de embeddings inicializado con modelo: {model_name}")
        except Exception as e:
            logger.error(f"Error al inicializar el cliente de OpenAI: {e}")
            raise ConnectionError(f"Error al conectar con OpenAI para embeddings: {str(e)}") from e
    
    def generate_embedding(self, text: str) -> List[float]:
        """Genera un embedding para un texto.
        
        Args:
            text: Texto para el que generar el embedding.
            
        Returns:
            List[float]: Vector de embedding.
        """
        if not text or not text.strip():
            logger.warning("Se intentó generar un embedding para un texto vacío")
            return [0.0] * 1536  # Dimensión predeterminada para compatibilidad
        
        try:
            # Limpiar y preparar el texto
            text = text.replace("\n", " ").strip()
            
            logger.info(f"Generando embedding con modelo {self.model_name}")
            
            # Llamar a la API de OpenAI
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            # Extraer el embedding
            embedding = response.data[0].embedding
            
            logger.info(f"Embedding generado correctamente. Dimensiones: {len(embedding)}")
            return embedding
            
        except Exception as e:
            error_msg = f"Error al generar embedding: {str(e)}"
            error_stack = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_stack}")
            raise ValueError(error_msg) from e 