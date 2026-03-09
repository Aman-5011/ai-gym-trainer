document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById('chat-panel');
    const toggle = document.getElementById('chat-toggle');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    // Toggle Panel
    toggle.onclick = () => {
        panel.classList.toggle('hidden');
        if (!panel.classList.contains('hidden')) loadHistory();
    };

    document.getElementById('close-chat').onclick = () => panel.classList.add('hidden');

    // FIX: Changed URL to '/api/chat' and added method: 'GET'
    async function loadHistory() {
        const res = await fetch('/api/chat'); 
        const history = await res.json();
        messages.innerHTML = '';
        history.forEach(h => appendMessage(h.sender, h.message));
        messages.scrollTop = messages.scrollHeight;
    }

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `msg ${sender}`;
        div.innerText = text; // Safer than innerHTML
        messages.appendChild(div);
    }

    // FIX: Changed URL to '/api/chat'
    document.getElementById('send-btn').onclick = async () => {
        const text = input.value.trim();
        if (!text) return;
        
        input.value = '';
        appendMessage('user', text);
        messages.scrollTop = messages.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            if(data.response) {
                appendMessage('ai', data.response);
            }
        } catch (err) {
            console.error("Chat error:", err);
        }
        messages.scrollTop = messages.scrollHeight;
    };

    // FIX: Changed URL to '/api/chat' and added method: 'DELETE'
    document.getElementById('reset-chat').onclick = async () => {
        if (confirm("Clear all chat history?")) {
            await fetch('/api/chat', { method: 'DELETE' });
            messages.innerHTML = '';
        }
    };
});