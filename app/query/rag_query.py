"""
Sistema de consultas RAG.
Este módulo proporciona funciones para realizar consultas RAG utilizando la base de datos vectorial.
"""

import logging
import json
import time
import traceback
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

from app.document_processing.embeddings import EmbeddingGenerator
from app.database.vector_store import VectorDatabase
from app.config.settings import LLM_MODEL, OPENAI_API_KEY
from app.utils.performance_metrics import performance_tracker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGQuerySystem:
    """Clase para realizar consultas RAG utilizando la base de datos vectorial."""
    
    def __init__(self, model_name: str = LLM_MODEL, api_key: str = OPENAI_API_KEY):
        """Inicializa el sistema de consultas RAG.
        
        Args:
            model_name: Nombre del modelo de lenguaje.
            api_key: Clave API de OpenAI.
        """
        # Validar API key de OpenAI
        if not api_key:
            logger.error("No se ha proporcionado la clave API de OpenAI")
            raise ValueError("No se ha proporcionado la clave API de OpenAI")
            
        self.embedding_generator = EmbeddingGenerator()
        
        try:
            self.vector_db = VectorDatabase()
        except Exception as e:
            logger.error(f"Error al inicializar la base de datos vectorial: {e}")
            raise ConnectionError(f"Error al conectar con la base de datos vectorial: {str(e)}") from e
            
        try:
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Error al inicializar el modelo de lenguaje: {e}")
            raise ConnectionError(f"Error al conectar con OpenAI: {str(e)}") from e
        
        # Asignar el rastreador de rendimiento
        self.performance_tracker = performance_tracker
        
        # Plantilla para el prompt de RAG
        self.prompt_template = ChatPromptTemplate.from_template(
            """Eres un asistente útil que responde preguntas basándose únicamente en el contexto proporcionado.
            
            Contexto:
            {context}
            
            Pregunta: {question}
            
            Instrucciones importantes:
            1. Responde solo con información que esté presente en el contexto proporcionado.
            2. Si el contexto no contiene la información necesaria para responder, di "No tengo suficiente información para responder a esta pregunta."
            3. No uses conocimiento externo o general que no esté en el contexto.
            4. Proporciona respuestas detalladas y precisas basadas únicamente en el contexto.
            5. Cita las fuentes de información cuando sea posible, refiriéndote al nombre del documento y número de fragmento.
            6. Si hay información contradictoria en el contexto, señálala y explica las diferentes perspectivas.
            
            Respuesta:"""
        )
    
    def query(self, query_text: str, similarity_threshold: float = 0.1, max_sources: int = 5) -> Dict[str, Any]:
        """Realiza una consulta al sistema RAG.
        
        Args:
            query_text: Texto de la consulta.
            similarity_threshold: Umbral de similitud para incluir documentos.
            max_sources: Número máximo de fuentes a recuperar.
            
        Returns:
            Dict: Resultado de la consulta, incluyendo la respuesta y las fuentes.
        """
        start_time = time.time()
        
        try:
            # Generar embedding para la consulta
            with self.performance_tracker.track("generate_query_embedding"):
                try:
                    query_embedding = self.embedding_generator.generate_embedding(query_text)
                except Exception as e:
                    logger.error(f"Error al generar embedding para la consulta: {e}")
                    raise ValueError(f"Error al generar embedding para la consulta: {str(e)}")
            
            # Buscar documentos relevantes
            with self.performance_tracker.track("retrieve_documents"):
                try:
                    documents = self.vector_db.similarity_search_with_score(
                        query_embedding=query_embedding,
                        similarity_threshold=similarity_threshold,
                        max_documents=max_sources
                    )
                except Exception as e:
                    logger.error(f"Error al buscar documentos relevantes: {e}")
                    error_stack = traceback.format_exc()
                    logger.error(f"Stack trace: {error_stack}")
                    raise ConnectionError(f"Error al buscar documentos en la base de datos: {str(e)}")
            
            if not documents:
                logger.info("No se encontraron documentos relevantes para la consulta.")
                return {
                    "answer": "No encontré información relevante para responder a tu pregunta. Por favor, intenta reformularla o consulta sobre otro tema.",
                    "sources": [],
                    "metadata": {
                        "query_time": time.time() - start_time,
                        "documents_retrieved": 0
                    }
                }
            
            # Preparar contexto para el LLM
            with self.performance_tracker.track("prepare_context"):
                context_docs = []
                for doc, score in documents:
                    context_docs.append(doc)
                
                # Crear texto de contexto
                context_text = "\n\n".join([f"Documento: {i+1}\n{doc.page_content}" for i, doc in enumerate(context_docs)])
            
            # Generar respuesta con el LLM
            with self.performance_tracker.track("generate_response"):
                try:
                    chain = self.prompt_template | self.llm
                    response = chain.invoke({"context": context_text, "question": query_text})
                    answer = response.content
                except Exception as e:
                    logger.error(f"Error al generar respuesta con el LLM: {e}")
                    raise ValueError(f"Error al generar respuesta: {str(e)}")
            
            # Guardar la consulta en la base de datos
            try:
                self.vector_db.save_query(query_text, answer)
            except Exception as e:
                logger.warning(f"Error al guardar la consulta: {e}")
            
            # Preparar el resultado
            result = {
                "answer": answer,
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity": score
                    }
                    for doc, score in documents
                ],
                "metadata": {
                    "query_time": time.time() - start_time,
                    "documents_retrieved": len(documents)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error al procesar la consulta: {e}")
            error_stack = traceback.format_exc()
            logger.error(f"Stack trace: {error_stack}")
            return {
                "answer": f"Lo siento, ha ocurrido un error al procesar tu consulta: {str(e)}",
                "sources": [],
                "metadata": {
                    "error": str(e),
                    "error_stack": error_stack,
                    "query_time": time.time() - start_time
                }
            } 