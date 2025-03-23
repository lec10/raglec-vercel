"""
Gestión de la base de datos vectorial.
Este módulo proporciona funciones para gestionar documentos y embeddings en la base de datos vectorial.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from langchain.schema import Document

from app.config.settings import SUPABASE_COLLECTION_NAME
from app.database.supabase_client import get_supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class VectorDatabase:
    """Clase para gestionar la base de datos vectorial."""
    
    def __init__(self, collection_name: str = None):
        """Inicializa la base de datos vectorial.
        
        Args:
            collection_name: Nombre de la colección a utilizar. Si no se proporciona,
                             se utiliza el valor de SUPABASE_COLLECTION_NAME.
        """
        self.collection_name = collection_name or SUPABASE_COLLECTION_NAME
        self.supabase_store = get_supabase_client()
        self.supabase = self.supabase_store.get_client()
        logger.info(f"Base de datos vectorial inicializada con colección: {self.collection_name}")
    
    def similarity_search_with_score(
        self, 
        query_embedding: List[float], 
        similarity_threshold: float = 0.1, 
        max_documents: int = 5
    ) -> List[Tuple[Document, float]]:
        """Realiza una búsqueda por similitud de vectores.
        
        Args:
            query_embedding: Embedding de la consulta.
            similarity_threshold: Umbral de similitud para incluir documentos.
            max_documents: Número máximo de documentos a recuperar.
            
        Returns:
            List[Tuple[Document, float]]: Lista de documentos con sus puntuaciones de similitud.
        """
        try:
            # Llamar a la función match_documents en Supabase
            response = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": similarity_threshold,
                    "match_count": max_documents
                }
            ).execute()
            
            if not response.data:
                logger.info("No se encontraron documentos que coincidan con la consulta")
                return []
            
            # Convertir los resultados en objetos Document de LangChain
            documents_with_scores = []
            for item in response.data:
                # Extraer el contenido y los metadatos
                content = item.get("content", "")
                metadata = item.get("metadata", {})
                similarity = item.get("similarity", 0.0)
                
                # Crear el documento
                doc = Document(page_content=content, metadata=metadata)
                
                # Añadir a la lista
                documents_with_scores.append((doc, similarity))
            
            return documents_with_scores
            
        except Exception as e:
            logger.error(f"Error al realizar búsqueda por similitud: {e}")
            raise 