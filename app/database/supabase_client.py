"""
Cliente de Supabase para la aplicación.
"""

import logging
import re
from supabase import create_client, Client
from app.config.settings import SUPABASE_URL, SUPABASE_KEY

# Configurar logging
logger = logging.getLogger(__name__)

class SupabaseStore:
    """Clase para gestionar la conexión con Supabase."""
    
    def __init__(self, url: str = None, key: str = None):
        """Inicializa la conexión con Supabase.
        
        Args:
            url: URL de Supabase. Si no se proporciona, se utiliza el valor de SUPABASE_URL.
            key: Clave API de Supabase. Si no se proporciona, se utiliza el valor de SUPABASE_KEY.
        """
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        
        if not self.url:
            logger.error("No se ha proporcionado la URL de Supabase")
            raise ValueError("No se ha proporcionado la URL de Supabase")
            
        if not self.key:
            logger.error("No se ha proporcionado la clave API de Supabase")
            raise ValueError("No se ha proporcionado la clave API de Supabase")
        
        # Formatear y validar URL de Supabase
        self._format_and_validate_supabase_url()
        
        self.client = None
        self._connect()
    
    def _format_and_validate_supabase_url(self):
        """Formatea y valida la URL de Supabase."""
        # Eliminar cualquier barra diagonal al final
        self.url = self.url.rstrip('/')
        
        # Asegurarse de que la URL comienza con https://
        if not self.url.startswith('https://'):
            if self.url.startswith('http://'):
                self.url = 'https://' + self.url[7:]
            else:
                self.url = 'https://' + self.url
                
        # Verificar que la URL termine con .supabase.co
        if not '.supabase.co' in self.url:
            error_msg = f"La URL de Supabase '{self.url}' no es válida. Debe incluir '.supabase.co'."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log para depuración
        logger.info(f"URL de Supabase formateada: {self.url}")
    
    def _connect(self):
        """Establece la conexión con Supabase."""
        try:
            # Extraer el ID del proyecto de la URL (el dominio antes de .supabase.co)
            project_id_match = re.search(r'https?://([^\.]+)\.supabase\.co', self.url)
            
            if not project_id_match:
                logger.error(f"No se pudo extraer el ID del proyecto de la URL: {self.url}")
                raise ValueError(f"URL de Supabase inválida. Debe tener el formato 'https://[proyecto-id].supabase.co'")
            
            project_id = project_id_match.group(1)
            
            # Construir la URL exactamente como la espera la biblioteca
            formatted_url = f"https://{project_id}.supabase.co"
            
            logger.info(f"Intentando conectar a Supabase URL: {formatted_url}")
            
            # Usar la URL formateada para crear el cliente
            self.client = create_client(formatted_url, self.key)
            logger.info("Conexión con Supabase establecida")
        except Exception as e:
            error_msg = f"Error al conectar con Supabase: {str(e)}"
            logger.error(error_msg)
            # Log adicional para depuración
            logger.error(f"URL original: '{self.url}'")
            logger.error(f"Key utilizada (primeros 5 caracteres): '{self.key[:5]}...'")
            raise ConnectionError(error_msg) from e
    
    def get_client(self) -> Client:
        """Obtiene el cliente de Supabase.
        
        Returns:
            Client: Cliente de Supabase.
        """
        if not self.client:
            self._connect()
        
        return self.client

def get_supabase_client(url: str = None, key: str = None) -> SupabaseStore:
    """Obtiene una instancia de SupabaseStore.
    
    Args:
        url: URL de Supabase. Si no se proporciona, se utiliza el valor de SUPABASE_URL.
        key: Clave API de Supabase. Si no se proporciona, se utiliza el valor de SUPABASE_KEY.
        
    Returns:
        SupabaseStore: Instancia de SupabaseStore.
    """
    return SupabaseStore(url, key) 