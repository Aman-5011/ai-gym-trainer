document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById('chat-panel');
    const toggle = document.getElementById('chat-toggle');
    const input = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');

    // --- Panel Toggle ---
    toggle.onclick = () => {
        panel.classList.toggle('hidden');
        if (!panel.classList.contains('hidden')) loadHistory();
    };

    document.getElementById('close-chat').onclick = () => panel.classList.add('hidden');

    // --- API Logic ---
    async function loadHistory() {
        try {
            const res = await fetch('/api/chat'); 
            const history = await res.json();
            messages.innerHTML = '';
            history.forEach(h => appendMessage(h.sender, h.message));
            messages.scrollTop = messages.scrollHeight;
        } catch (err) { console.error("History error:", err); }
    }

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `msg ${sender}`;
        div.innerText = text;
        messages.appendChild(div);
    }

    document.getElementById('send-btn').onclick = sendMsg;
    input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMsg(); });

    async function sendMsg() {
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
            if(data.response) appendMessage('ai', data.response);
        } catch (err) { appendMessage('ai', "Quota full or connection error."); }
        
        messages.scrollTop = messages.scrollHeight;
    }

    document.getElementById('reset-chat').onclick = async () => {
        if (confirm("Clear all chat history?")) {
            await fetch('/api/chat', { method: 'DELETE' });
            messages.innerHTML = '';
        }
    };

    // --- Reshaping (Dragging) Logic ---
    // Create the handle dynamically to follow SRP
    const handle = document.createElement('div');
    handle.className = 'resize-handle';
    panel.appendChild(handle);

    handle.addEventListener('mousedown', initResize, false);

    function initResize(e) {
        window.addEventListener('mousemove', Resize, false);
        window.addEventListener('mouseup', stopResize, false);
    }

    function Resize(e) {
        // Calculate new width/height based on mouse position relative to fixed bottom-right
        const newWidth = window.innerWidth - e.clientX - (window.innerWidth - panel.getBoundingClientRect().right);
        const newHeight = window.innerHeight - e.clientY - (window.innerHeight - panel.getBoundingClientRect().bottom);
        
        if (newWidth > 300) panel.style.width = newWidth + 'px';
        if (newHeight > 400) panel.style.height = newHeight + 'px';
    }

    function stopResize(e) {
        window.removeEventListener('mousemove', Resize, false);
        window.removeEventListener('mouseup', stopResize, false);
    }
});