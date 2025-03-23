from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback

# Añadir directorios al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.query.rag_query import RAGQuerySystem
from app.config.settings import load_environment_variables

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Cargar variables de entorno
        load_environment_variables()
        
        # Obtener el cuerpo de la solicitud
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Obtener la consulta
        query = data.get('query', '')
        
        if not query:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': 'La consulta está vacía'}
            self.wfile.write(json.dumps(response).encode())
            return
        
        try:
            # Inicializar el sistema RAG
            rag_system = RAGQuerySystem()
            
            # Procesar la consulta
            result = rag_system.query(query)
            
            # Enviar respuesta
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            # Obtener el traceback completo
            error_traceback = traceback.format_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'error': str(e),
                'traceback': error_traceback,
                'api_key_set': bool(os.getenv("OPENAI_API_KEY")),
                'supabase_url_set': bool(os.getenv("SUPABASE_URL")),
                'supabase_key_set': bool(os.getenv("SUPABASE_KEY"))
            }
            self.wfile.write(json.dumps(response).encode()) 