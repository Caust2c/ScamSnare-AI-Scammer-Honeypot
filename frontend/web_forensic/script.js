const API_CONFIG = {
    url: 'http://localhost:8000/detect',
    key: '123456' //CHANGE THIS TO MATCH CONFIG.PY
};

let sessionState = {
    conversationId: generateSessionId(),
    history: [],
    metrics: {
        turns: 0,
        confidence: 0,
        intelligence: 0,
        classification: 'UNKNOWN'
    }
};

const DOM = {
    sessionId: document.getElementById('session-id'),
    currentTime: document.getElementById('current-time'),
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    turnCount: document.getElementById('turn-count'),
    scamConfidence: document.getElementById('scam-confidence'),
    confidenceBar: document.getElementById('confidence-bar'),
    intelCount: document.getElementById('intel-count'),
    classification: document.getElementById('classification'),
    conversationArea: document.getElementById('conversation-area'),
    processingIndicator: document.getElementById('processing-indicator'),
    analysisContent: document.getElementById('analysis-content'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn')
};

function init() {
    DOM.sessionId.textContent = sessionState.conversationId;
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
    
    DOM.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function generateSessionId() {
    const prefix = 'SIP';
    const timestamp = Date.now().toString(36).toUpperCase();
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    return `${prefix}-${timestamp}-${random}`;
}

function updateTimestamp() {
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    DOM.currentTime.textContent = timestamp;
}

function getMessageTimestamp() {
    const now = new Date();
    return now.toTimeString().substring(0, 8);
}

async function sendMessage() {
    const message = DOM.messageInput.value.trim();
    if (!message) return;

    disableInput();
    showProcessing();
    clearEmptyState();
    
    addMessageToUI('threat', message);
    DOM.messageInput.value = '';

    try {
        const response = await fetch(API_CONFIG.url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_CONFIG.key
            },
            body: JSON.stringify({
                conversation_id: sessionState.conversationId,
                message: message,
                history: sessionState.history
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        
        sessionState.history.push({
            role: 'scammer',
            content: message,
            timestamp: new Date().toISOString()
        });

        sessionState.history.push({
            role: 'agent',
            content: data.response_message,
            timestamp: new Date().toISOString()
        });

        addMessageToUI('agent', data.response_message);
        updateMetrics(data);
        updateAnalysisPanel(data);
        
    } catch (error) {
        console.error('Communication Error:', error);
        showError(error.message);
    } finally {
        hideProcessing();
        enableInput();
    }
}

function addMessageToUI(source, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${source}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const sourceLabel = document.createElement('span');
    sourceLabel.className = `message-source ${source}`;
    sourceLabel.textContent = source === 'threat' ? 'THREAT ACTOR' : 'HONEYPOT AGENT';
    
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = getMessageTimestamp();
    
    header.appendChild(sourceLabel);
    header.appendChild(time);
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(messageContent);
    
    DOM.conversationArea.appendChild(messageDiv);
    DOM.conversationArea.scrollTop = DOM.conversationArea.scrollHeight;
}

function updateMetrics(data) {
    sessionState.metrics.turns = data.engagement_metrics.total_turns;
    sessionState.metrics.confidence = data.confidence_score;
    sessionState.metrics.intelligence = data.engagement_metrics.intelligence_items_found;
    
    if (data.scam_detected) {
        sessionState.metrics.classification = data.confidence_score > 0.7 ? 'HIGH THREAT' : 'MEDIUM THREAT';
    } else {
        sessionState.metrics.classification = 'LOW THREAT';
    }
    
    DOM.turnCount.textContent = sessionState.metrics.turns;
    DOM.scamConfidence.textContent = Math.round(sessionState.metrics.confidence * 100) + '%';
    DOM.confidenceBar.style.width = (sessionState.metrics.confidence * 100) + '%';
    DOM.intelCount.textContent = sessionState.metrics.intelligence;
    
    DOM.classification.textContent = sessionState.metrics.classification;
    DOM.classification.className = 'metric-value';
    
    if (sessionState.metrics.classification.includes('HIGH')) {
        DOM.classification.classList.add('status-threat');
    } else if (sessionState.metrics.classification.includes('LOW')) {
        DOM.classification.classList.add('status-safe');
    }
}

function updateAnalysisPanel(data) {
    let html = '';
    
    html += '<div class="analysis-section">';
    html += '<div class="analysis-section-title">THREAT ASSESSMENT</div>';
    html += `<div class="threat-indicator ${data.scam_detected ? 'detected' : 'safe'}">`;
    html += data.scam_detected ? 'SCAM DETECTED' : 'NO IMMEDIATE THREAT';
    html += '</div>';
    html += `<p style="margin-top: 10px; font-size: 11px; color: var(--text-secondary);">`;
    html += `Confidence Level: ${Math.round(data.confidence_score * 100)}%</p>`;
    html += `<p style="font-size: 11px; color: var(--text-secondary);">`;
    html += `Agent Status: ${data.agent_activated ? 'ENGAGED' : 'MONITORING'}</p>`;
    html += '</div>';
    
    const intel = data.extracted_intelligence;
    const hasIntel = intel.bank_accounts?.length || intel.upi_ids?.length || 
                     intel.phone_numbers?.length || intel.urls?.length;
    
    if (hasIntel) {
        html += '<div class="analysis-section">';
        html += '<div class="analysis-section-title">EXTRACTED INTELLIGENCE</div>';
        
        if (intel.bank_accounts?.length) {
            intel.bank_accounts.forEach(account => {
                html += '<div class="intel-item">';
                html += '<div class="intel-label">BANK ACCOUNT</div>';
                html += `<div class="intel-value">${account}</div>`;
                html += '</div>';
            });
        }
        
        if (intel.upi_ids?.length) {
            intel.upi_ids.forEach(upi => {
                html += '<div class="intel-item">';
                html += '<div class="intel-label">UPI IDENTIFIER</div>';
                html += `<div class="intel-value">${upi}</div>`;
                html += '</div>';
            });
        }
        
        if (intel.phone_numbers?.length) {
            intel.phone_numbers.forEach(phone => {
                html += '<div class="intel-item">';
                html += '<div class="intel-label">PHONE NUMBER</div>';
                html += `<div class="intel-value">${phone}</div>`;
                html += '</div>';
            });
        }
        
        if (intel.urls?.length) {
            intel.urls.forEach(url => {
                html += '<div class="intel-item">';
                html += '<div class="intel-label">SUSPICIOUS URL</div>';
                html += `<div class="intel-value">${url}</div>`;
                html += '</div>';
            });
        }
        
        html += '</div>';
    }
    
    html += '<div class="analysis-section">';
    html += '<div class="analysis-section-title">ENGAGEMENT METRICS</div>';
    html += `<p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 5px;">`;
    html += `Total Turns: ${data.engagement_metrics.total_turns}</p>`;
    html += `<p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 5px;">`;
    html += `Agent Turns: ${data.engagement_metrics.agent_turns}</p>`;
    html += `<p style="font-size: 11px; color: var(--text-secondary);">`;
    html += `Duration: ${data.engagement_metrics.conversation_duration_seconds}s</p>`;
    html += '</div>';
    
    DOM.analysisContent.innerHTML = html;
}

function clearEmptyState() {
    const emptyState = DOM.conversationArea.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
}

function clearConversation() {
    if (!confirm('Clear current session and reset all data?')) {
        return;
    }
    
    sessionState.conversationId = generateSessionId();
    sessionState.history = [];
    sessionState.metrics = {
        turns: 0,
        confidence: 0,
        intelligence: 0,
        classification: 'UNKNOWN'
    };
    
    DOM.sessionId.textContent = sessionState.conversationId;
    
    DOM.conversationArea.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon"></div>
            <p>NO ACTIVE CONVERSATION</p>
            <span>Initiate contact to begin analysis</span>
        </div>
    `;
    
    DOM.analysisContent.innerHTML = `
        <div class="analysis-placeholder">
            <p>Awaiting data...</p>
        </div>
    `;
    
    DOM.turnCount.textContent = '0';
    DOM.scamConfidence.textContent = '0%';
    DOM.confidenceBar.style.width = '0%';
    DOM.intelCount.textContent = '0';
    DOM.classification.textContent = 'UNKNOWN';
    DOM.classification.className = 'metric-value status-unknown';
}

function showProcessing() {
    DOM.processingIndicator.classList.add('active');
}

function hideProcessing() {
    DOM.processingIndicator.classList.remove('active');
}

function disableInput() {
    DOM.messageInput.disabled = true;
    DOM.sendBtn.disabled = true;
}

function enableInput() {
    DOM.messageInput.disabled = false;
    DOM.sendBtn.disabled = false;
    DOM.messageInput.focus();
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message system';
    errorDiv.innerHTML = `
        <div class="message-header">
            <span class="message-source" style="background: rgba(255, 71, 87, 0.1); color: var(--accent-red); border: 1px solid rgba(255, 71, 87, 0.3);">SYSTEM ERROR</span>
            <span class="message-time">${getMessageTimestamp()}</span>
        </div>
        <div class="message-content" style="border-left: 3px solid var(--accent-red);">
            ${message}
        </div>
    `;
    DOM.conversationArea.appendChild(errorDiv);
    DOM.conversationArea.scrollTop = DOM.conversationArea.scrollHeight;
}

document.addEventListener('DOMContentLoaded', init);
