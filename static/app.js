let conversationId = generateUUID();

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function addMessage(content, isUser = false) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return messageDiv;
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById('messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant-message typing-indicator';
    typingDiv.id = 'typing';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typing');
    if (typing) {
        typing.remove();
    }
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, true);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
        
        removeTypingIndicator();
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = addMessage('', false);
        let fullText = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            fullText += chunk;
            assistantMessage.textContent = fullText;
            
            // Auto-scroll
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', false);
        console.error('Error:', error);
    }
}

// Event listeners
document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Welcome message
window.addEventListener('load', () => {
    addMessage('Hello! I\'m your AI travel planning assistant. Tell me where you\'d like to go or what kind of trip you\'re interested in, and I\'ll help you plan the perfect adventure!', false);
});
