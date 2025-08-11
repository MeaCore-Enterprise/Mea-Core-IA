// MEA-Core Local AI Assistant - Frontend JavaScript

class MEACore {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadSystemStats();
        this.pollProgress();
        
        console.log('MEA-Core initialized');
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebarOpenBtn = document.getElementById('sidebarOpenBtn');
        
        // Upload elements
        this.textUploadBtn = document.getElementById('textUploadBtn');
        this.pdfUpload = document.getElementById('pdfUpload');
        
        // Modal elements
        this.textModal = document.getElementById('textModal');
        this.textModalClose = document.getElementById('textModalClose');
        this.textTitle = document.getElementById('textTitle');
        this.textContent = document.getElementById('textContent');
        this.textSubmitBtn = document.getElementById('textSubmitBtn');
        this.textCancelBtn = document.getElementById('textCancelBtn');
        
        // Progress elements
        this.progressContainer = document.getElementById('progressContainer');
        this.progressText = document.getElementById('progressText');
        this.progressPercent = document.getElementById('progressPercent');
        this.progressFill = document.getElementById('progressFill');
        
        // Status elements
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.docCount = document.getElementById('docCount');
        this.avgLength = document.getElementById('avgLength');
        this.systemStatus = document.getElementById('systemStatus');
    }

    attachEventListeners() {
        // Chat functionality
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Sidebar controls
        this.sidebarToggle.addEventListener('click', () => this.closeSidebar());
        this.sidebarOpenBtn.addEventListener('click', () => this.openSidebar());

        // Upload controls
        this.textUploadBtn.addEventListener('click', () => this.openTextModal());
        this.pdfUpload.addEventListener('change', (e) => this.handlePDFUpload(e));

        // Modal controls
        this.textModalClose.addEventListener('click', () => this.closeTextModal());
        this.textCancelBtn.addEventListener('click', () => this.closeTextModal());
        this.textSubmitBtn.addEventListener('click', () => this.submitTextDocument());

        // Close modal when clicking outside
        this.textModal.addEventListener('click', (e) => {
            if (e.target === this.textModal) {
                this.closeTextModal();
            }
        });

        // Auto-resize chat input
        this.chatInput.addEventListener('input', () => this.autoResizeInput());
    }

    async sendMessage() {
        const query = this.chatInput.value.trim();
        if (!query) return;

        // Disable input while processing
        this.chatInput.disabled = true;
        this.sendButton.disabled = true;

        // Add user message to chat
        this.addMessage('user', query);
        this.chatInput.value = '';

        try {
            // Show typing indicator
            const typingMessage = this.addMessage('system', '', true);
            this.showTyping(typingMessage);

            // Send query to backend
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ q: query, k: 6 })
            });

            const data = await response.json();

            // Remove typing indicator
            typingMessage.remove();

            if (data.error) {
                this.addMessage('system', `Error: ${data.error}`, false, 'error');
            } else {
                this.addQueryResponse(data);
            }

        } catch (error) {
            console.error('Query error:', error);
            this.addMessage('system', 'Sorry, I encountered an error while processing your query. Please try again.', false, 'error');
        } finally {
            // Re-enable input
            this.chatInput.disabled = false;
            this.sendButton.disabled = false;
            this.chatInput.focus();
        }
    }

    addMessage(type, content, isTyping = false, variant = 'default') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const icon = document.createElement('i');
        icon.className = `message-icon fas ${type === 'user' ? 'fa-user' : 'fa-robot'}`;

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';

        if (isTyping) {
            textDiv.innerHTML = '<div class="loading"></div>';
        } else {
            textDiv.innerHTML = content;
        }

        messageContent.appendChild(icon);
        messageContent.appendChild(textDiv);
        messageDiv.appendChild(messageContent);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    addQueryResponse(data) {
        const { query, results, summary, total, intent, grouped_results, entities, key_phrases, suggestions } = data;

        let responseHTML = `<h3><i class="fas fa-brain"></i> AI Analysis Results</h3>`;
        responseHTML += `<p><strong>Query:</strong> ${query}</p>`;
        
        // Show intent analysis
        if (intent) {
            responseHTML += `<p><strong>Intent Detected:</strong> <span class="intent-badge">${intent}</span></p>`;
        }
        
        // Show entities if found
        if (entities && Object.keys(entities).length > 0) {
            responseHTML += `<div class="entities-container">`;
            responseHTML += `<h4><i class="fas fa-tags"></i> Entities Found:</h4>`;
            for (const [entityType, entityList] of Object.entries(entities)) {
                if (entityList.length > 0) {
                    responseHTML += `<p><strong>${entityType}:</strong> ${entityList.slice(0, 3).join(', ')}</p>`;
                }
            }
            responseHTML += `</div>`;
        }
        
        // Show key phrases
        if (key_phrases && key_phrases.length > 0) {
            responseHTML += `<div class="key-phrases-container">`;
            responseHTML += `<h4><i class="fas fa-key"></i> Key Phrases:</h4>`;
            responseHTML += `<p>${key_phrases.slice(0, 5).join(' • ')}</p>`;
            responseHTML += `</div>`;
        }
        
        if (summary && summary !== "No relevant content found.") {
            responseHTML += `<div class="summary-container">`;
            responseHTML += `<h4><i class="fas fa-lightbulb"></i> AI Summary:</h4>`;
            responseHTML += `<p>${summary}</p>`;
            responseHTML += `</div>`;
        }

        if (results && results.length > 0) {
            // Show grouped results if available
            if (grouped_results && Object.keys(grouped_results).length > 1) {
                responseHTML += `<div class="grouped-results-container">`;
                responseHTML += `<h4><i class="fas fa-layer-group"></i> Results by Category:</h4>`;
                
                for (const [category, categoryResults] of Object.entries(grouped_results)) {
                    if (categoryResults.length > 0) {
                        responseHTML += `<div class="category-group">`;
                        responseHTML += `<h5 class="category-title"><i class="fas fa-folder"></i> ${category.toUpperCase()} (${categoryResults.length})</h5>`;
                        
                        categoryResults.slice(0, 2).forEach((result) => {
                            responseHTML += `
                                <div class="result-item category-${category}">
                                    <div class="result-title">
                                        <span>${result.title}</span>
                                        <span class="result-score">Score: ${result.score}</span>
                                    </div>
                                    <div class="result-text">${result.text}</div>
                                    <div class="result-meta">Category: ${result.category}</div>
                                </div>
                            `;
                        });
                        responseHTML += `</div>`;
                    }
                }
                responseHTML += `</div>`;
            } else {
                // Standard results display
                responseHTML += `<div class="results-container">`;
                responseHTML += `<p style="margin-bottom: 1rem; color: var(--text-dim);">Found ${total} relevant chunks (showing top ${results.length}):</p>`;
                
                results.forEach((result, index) => {
                    responseHTML += `
                        <div class="result-item">
                            <div class="result-title">
                                <span>${result.title}</span>
                                <span class="result-score">Score: ${result.score}</span>
                            </div>
                            <div class="result-text">${result.text}</div>
                            <div class="result-meta">Category: ${result.category || 'general'}</div>
                        </div>
                    `;
                });
                responseHTML += `</div>`;
            }
            
            // Show AI suggestions
            if (suggestions && suggestions.length > 0) {
                responseHTML += `<div class="suggestions-container">`;
                responseHTML += `<h4><i class="fas fa-magic"></i> AI Suggestions:</h4>`;
                responseHTML += `<ul>`;
                suggestions.slice(0, 3).forEach(suggestion => {
                    responseHTML += `<li>${suggestion}</li>`;
                });
                responseHTML += `</ul>`;
                responseHTML += `</div>`;
            }
        } else {
            responseHTML += `<p style="color: var(--text-dim);">No documents found. Try adding some documents to your knowledge base first.</p>`;
            
            if (suggestions && suggestions.length > 0) {
                responseHTML += `<div class="suggestions-container">`;
                responseHTML += `<h4><i class="fas fa-lightbulb"></i> Suggestions:</h4>`;
                responseHTML += `<ul>`;
                suggestions.forEach(suggestion => {
                    responseHTML += `<li>${suggestion}</li>`;
                });
                responseHTML += `</ul>`;
                responseHTML += `</div>`;
            }
        }

        this.addMessage('system', responseHTML);
    }

    showTyping(messageElement) {
        const textDiv = messageElement.querySelector('.message-text');
        let dots = '';
        const interval = setInterval(() => {
            dots = dots.length >= 3 ? '' : dots + '.';
            textDiv.innerHTML = `<div style="display: flex; align-items: center; gap: 0.5rem;"><div class="loading"></div>Thinking${dots}</div>`;
        }, 500);

        // Store interval to clear it later
        messageElement.typingInterval = interval;
    }

    async loadSystemStats() {
        try {
            // Load basic stats
            const response = await fetch('/health');
            const data = await response.json();
            
            this.docCount.textContent = data.docs_indexed || 0;
            this.avgLength.textContent = Math.round(data.avgdl || 0);
            this.systemStatus.textContent = data.status === 'ok' ? 'Ready' : 'Error';
            
            // Update status indicator
            if (data.status === 'ok') {
                this.statusDot.style.background = 'var(--success)';
                this.statusText.textContent = 'AI Ready';
            } else {
                this.statusDot.style.background = '#ff4444';
                this.statusText.textContent = 'Error';
            }
            
            // Load advanced stats
            try {
                const advancedResponse = await fetch('/stats/advanced');
                const advancedData = await advancedResponse.json();
                this.updateAdvancedStats(advancedData);
            } catch (advError) {
                console.log('Advanced stats not available yet');
            }
            
        } catch (error) {
            console.error('Error loading system stats:', error);
            this.systemStatus.textContent = 'Offline';
            this.statusDot.style.background = '#ff4444';
            this.statusText.textContent = 'Offline';
        }
    }
    
    updateAdvancedStats(data) {
        // Update existing stats elements with advanced info
        if (data.basic) {
            this.docCount.textContent = data.basic.docs_indexed || 0;
            this.avgLength.textContent = data.basic.avg_document_length || 0;
        }
        
        // Add learning stats to status text
        if (data.learning && data.learning.queries_processed > 0) {
            this.systemStatus.textContent = `Learning (${data.learning.queries_processed} queries)`;
        }
    }
    
    async trainIntent(query, intent) {
        try {
            const response = await fetch('/learning/train', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    type: 'intent',
                    intent: intent,
                    strength: 1.0
                })
            });
            
            const data = await response.json();
            if (data.ok) {
                console.log('AI trained successfully:', data.message);
            }
        } catch (error) {
            console.error('Error training AI:', error);
        }
    }

    async pollProgress() {
        try {
            const response = await fetch('/progress');
            const progress = await response.json();
            
            if (progress.status === 'indexing') {
                this.showProgress(progress);
            } else if (progress.status === 'done') {
                this.hideProgress();
                this.loadSystemStats(); // Refresh stats
            } else {
                this.hideProgress();
            }
        } catch (error) {
            console.error('Error polling progress:', error);
        }

        // Poll every 1 second
        setTimeout(() => this.pollProgress(), 1000);
    }

    showProgress(progress) {
        const percent = Math.round((progress.processed / progress.total) * 100);
        
        this.progressContainer.style.display = 'block';
        this.progressText.textContent = `Processing document... (${progress.processed}/${progress.total})`;
        this.progressPercent.textContent = `${percent}%`;
        this.progressFill.style.width = `${percent}%`;
    }

    hideProgress() {
        this.progressContainer.style.display = 'none';
    }

    openTextModal() {
        this.textModal.classList.add('active');
        this.textTitle.value = '';
        this.textContent.value = '';
        this.textTitle.focus();
    }

    closeTextModal() {
        this.textModal.classList.remove('active');
    }

    async submitTextDocument() {
        const title = this.textTitle.value.trim() || 'Untitled Document';
        const text = this.textContent.value.trim();

        if (!text) {
            alert('Please enter some text content.');
            return;
        }

        try {
            this.textSubmitBtn.disabled = true;
            this.textSubmitBtn.textContent = 'Adding...';

            const formData = new FormData();
            formData.append('title', title);
            formData.append('text', text);

            const response = await fetch('/add_txt', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.ok) {
                this.closeTextModal();
                this.addMessage('system', `✅ Successfully added document: "${title}". Processing in background...`);
            } else {
                throw new Error(data.error || 'Failed to add document');
            }
        } catch (error) {
            console.error('Error adding text document:', error);
            alert(`Error: ${error.message}`);
        } finally {
            this.textSubmitBtn.disabled = false;
            this.textSubmitBtn.textContent = 'Add Document';
        }
    }

    async handlePDFUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Please select a PDF file.');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('title', file.name.replace('.pdf', ''));

            const response = await fetch('/add_pdf', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.ok) {
                this.addMessage('system', `✅ Successfully uploaded PDF: "${file.name}". Processing in background...`);
            } else {
                throw new Error(data.error || 'Failed to upload PDF');
            }
        } catch (error) {
            console.error('Error uploading PDF:', error);
            alert(`Error: ${error.message}`);
        } finally {
            // Clear the file input
            event.target.value = '';
        }
    }

    openSidebar() {
        this.sidebar.classList.add('active');
        this.sidebarOpenBtn.style.display = 'none';
    }

    closeSidebar() {
        this.sidebar.classList.remove('active');
        this.sidebarOpenBtn.style.display = 'flex';
    }

    autoResizeInput() {
        // Auto-resize functionality can be added here if needed
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.meaCore = new MEACore();
});
