document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    const responseContent = document.getElementById('response-content');
    const sourcesContent = document.getElementById('sources-content');
    const loadingIndicator = document.getElementById('loading');
    
    // Función para enviar la consulta
    async function sendQuery() {
        const query = queryInput.value.trim();
        
        if (!query) {
            alert('Por favor, ingresa una consulta');
            return;
        }
        
        // Mostrar indicador de carga
        loadingIndicator.classList.remove('hidden');
        responseContent.innerHTML = '';
        sourcesContent.innerHTML = '';
        
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
            
            // Capturar el texto de la respuesta para depuración
            const responseText = await response.text();
            let data;
            
            try {
                // Intentar parsear como JSON
                data = JSON.parse(responseText);
            } catch (parseError) {
                // Si no es JSON válido, mostrar el texto recibido
                responseContent.innerHTML = `
                    <p class="error">Error: La respuesta no es JSON válido</p>
                    <details>
                        <summary>Detalles de la respuesta</summary>
                        <pre>${responseText.substring(0, 500)}${responseText.length > 500 ? '...' : ''}</pre>
                    </details>
                `;
                loadingIndicator.classList.add('hidden');
                return;
            }
            
            if (!response.ok) {
                // Si hay un error en la respuesta, mostrar detalles completos
                let errorMessage = `<p class="error">Error del servidor (${response.status}):</p>`;
                
                if (data.error) {
                    errorMessage += `<p>${data.error}</p>`;
                }
                
                if (data.traceback) {
                    errorMessage += `<details>
                        <summary>Detalles técnicos</summary>
                        <pre>${data.traceback}</pre>
                    </details>`;
                }
                
                // Mostrar estado de las variables de entorno
                if (data.api_key_set !== undefined) {
                    errorMessage += `<p>Estado de configuración:</p>
                    <ul>
                        <li>API Key de OpenAI: ${data.api_key_set ? '✅ Configurada' : '❌ No configurada'}</li>
                        <li>URL de Supabase: ${data.supabase_url_set ? '✅ Configurada' : '❌ No configurada'}</li>
                        <li>Key de Supabase: ${data.supabase_key_set ? '✅ Configurada' : '❌ No configurada'}</li>
                    </ul>`;
                }
                
                responseContent.innerHTML = errorMessage;
                return;
            }
            
            // Mostrar respuesta exitosa
            responseContent.innerHTML = `<p>${data.answer || data.response || 'No se obtuvo respuesta'}</p>`;
            
            // Mostrar fuentes
            if (data.sources && data.sources.length > 0) {
                const sourcesList = document.createElement('ul');
                data.sources.forEach(source => {
                    const sourceItem = document.createElement('li');
                    sourceItem.innerHTML = `
                        <strong>${source.metadata?.filename || 'Documento'}</strong>
                        ${source.metadata?.chunk_index ? ` (Fragmento ${source.metadata.chunk_index})` : ''}
                        <p>${source.content ? source.content.substring(0, 200) + (source.content.length > 200 ? '...' : '') : 'Sin contenido'}</p>
                    `;
                    sourcesList.appendChild(sourceItem);
                });
                sourcesContent.appendChild(sourcesList);
            } else {
                sourcesContent.innerHTML = '<p>No hay fuentes disponibles</p>';
            }
        } catch (error) {
            // Error al realizar la petición
            responseContent.innerHTML = `
                <p class="error">Error de conexión: ${error.message}</p>
                <p>No se pudo conectar con el servidor. Verifique su conexión a internet o inténtelo más tarde.</p>
            `;
            console.error('Error completo:', error);
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    // Evento para el botón de enviar
    sendButton.addEventListener('click', sendQuery);
    
    // Evento para presionar Enter en el textarea
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });
}); 