"""
Módulo para rastrear métricas de rendimiento.
"""
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """Clase para rastrear métricas de rendimiento."""
    
    def __init__(self):
        """Inicializa el rastreador de rendimiento."""
        self.metrics = {}
    
    @contextmanager
    def track(self, operation_name):
        """Rastrea el tiempo de ejecución de una operación.
        
        Args:
            operation_name: Nombre de la operación a rastrear.
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            if operation_name not in self.metrics:
                self.metrics[operation_name] = []
            
            self.metrics[operation_name].append(duration)
            logger.debug(f"Operación '{operation_name}' completada en {duration:.4f} segundos")
    
    def get_metrics(self):
        """Obtiene las métricas de rendimiento.
        
        Returns:
            dict: Métricas de rendimiento.
        """
        result = {}
        
        for operation, times in self.metrics.items():
            result[operation] = {
                "count": len(times),
                "total_time": sum(times),
                "average_time": sum(times) / len(times) if times else 0,
                "min_time": min(times) if times else 0,
                "max_time": max(times) if times else 0
            }
        
        return result
    
    def reset(self):
        """Reinicia las métricas de rendimiento."""
        self.metrics = {}

# Instancia global del rastreador de rendimiento
performance_tracker = PerformanceTracker() 