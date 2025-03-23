document.addEventListener('DOMContentLoaded', function() {
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    const responseContent = document.getElementById('response-content');
    const sourcesContent = document.getElementById('sources-content');
    const loadingIndicator = document.getElementById('loading');
    
    // Asegurar que el indicador de carga esté oculto inicialmente
    loadingIndicator.classList.add('hidden');
    
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
            // Convertir los saltos de línea en <br> y aplicar formato para los párrafos
            const formattedAnswer = data.answer || data.response || 'No se obtuvo respuesta';
            const paragraphs = formattedAnswer.split('\n\n').filter(p => p.trim());
            
            const answerHtml = `
                <div class="answer-container">
                    ${paragraphs.map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`).join('')}
                </div>
            `;
            
            responseContent.innerHTML = answerHtml;
            
            // Mostrar fuentes con mejor formato
            if (data.sources && data.sources.length > 0) {
                const sourcesList = document.createElement('div');
                sourcesList.className = 'sources-list';
                
                data.sources.forEach((source, index) => {
                    const similarity = source.similarity ? Math.round(source.similarity * 100) : null;
                    const sourceItem = document.createElement('div');
                    sourceItem.className = 'source-item';
                    
                    sourceItem.innerHTML = `
                        <div class="source-header">
                            <h4>Fuente ${index + 1}${similarity ? ` <span class="similarity">(${similarity}% similitud)</span>` : ''}</h4>
                            <div class="source-meta">
                                ${source.metadata?.filename ? `<span class="filename">${source.metadata.filename}</span>` : ''}
                                ${source.metadata?.chunk_index ? `<span class="chunk">Fragmento ${source.metadata.chunk_index}</span>` : ''}
                            </div>
                        </div>
                        <div class="source-content">
                            ${source.content ? source.content.substring(0, 300) + (source.content.length > 300 ? '...' : '') : 'Sin contenido'}
                        </div>
                    `;
                    sourcesList.appendChild(sourceItem);
                });
                
                // Limpiar el contenido existente y agregar el nuevo
                sourcesContent.innerHTML = '<h3>Fuentes consultadas</h3>';
                sourcesContent.appendChild(sourcesList);
            } else {
                sourcesContent.innerHTML = '<p class="info-message">No hay fuentes disponibles para esta consulta</p>';
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