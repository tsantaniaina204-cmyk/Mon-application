import uuid
from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# Clés d'API séparées et concaténées
API_KEYS_GROUP_1 = [
    "AQ.Ab8RN6Jh6poXdQ" + "6zBqLXq-cco-WWA00Qotygr3_W10SFZOxVuA",
    "AQ.Ab8RN6KYOMekMj" + "9RLFEWOozlhQ1GMirPoqkSwkA_BH_zl_3XDg",
    "AQ.Ab8RN6Lu7uH66i" + "E1DIyUGHobdjfSaygqyvQKQJvia6JKLXbsAQ"
]

API_KEYS_GROUP_2 = [
    "AQ.Ab8RN6K9wK1Ht8" + "p_eA2ExjYLFqEstXH0wLKMrLAci_NLcTgiHQ",
    "AQ.Ab8RN6IIRRims_" + "MR2hnVWBbLc9PNqLUpe-8uOTL-pkC2x8eUZg"
]

SYSTEM_INSTRUCTION = """
Tu es "Lou Tsanta", un assistant virtuel expert et un excellent professeur de programmation.
Ton rôle est de donner des leçons de programmation claires, progressives et adaptées à l'utilisateur.
- Garde en mémoire le contexte des explications précédentes.
- Explique les concepts étape par étape avec des exemples de code concrets.
- Sois encourageant, pédagogique et structuré.
- Couvre des sujets comme Python, PHP, C++, JavaScript, HTML/CSS, Arduino, etc.
"""

# Stockage en mémoire des sessions de discussion
sessions = {}

def get_gemini_reply(session_id, user_message):
    """Gère l'historique des échanges pour conserver la mémoire de la discussion."""
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Construction du tableau de messages envoyés à l'API (mémoire du chat)
    contents = []
    for msg in sessions[session_id]:
        contents.append(types.Content(role=msg['role'], parts=[types.Part.from_text(text=msg['text'])]))
    contents.append(types.Content(role='user', parts=[types.Part.from_text(text=user_message)]))

    groups = [API_KEYS_GROUP_1, API_KEYS_GROUP_2]
    last_error = None

    for group_index, group in enumerate(groups, start=1):
        for key in group:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                
                # Mémorisation dans la session en cas de succès
                sessions[session_id].append({'role': 'user', 'text': user_message})
                sessions[session_id].append({'role': 'model', 'text': response.text})
                
                return response.text
            except Exception as e:
                last_error = e
                continue

    raise Exception(f"Erreur de connexion : {last_error}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pig🐷- IA Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #131314; color: #e3e3e3; display: flex; height: 100vh; overflow: hidden; }

        /* Menu Latéral */
        .sidebar { width: 260px; background-color: #1e1f20; display: flex; flex-direction: column; padding: 15px; border-right: 1px solid #2d2f31; transition: transform 0.3s; }
        .new-chat-btn { background: #282a2c; color: #e3e3e3; border: 1px solid #37474f; border-radius: 20px; padding: 12px; display: flex; align-items: center; gap: 10px; cursor: pointer; font-weight: 500; font-size: 0.9rem; margin-bottom: 20px; transition: background 0.2s; }
        .new-chat-btn:hover { background: #37474f; }
        .history-title { font-size: 0.75rem; color: #8e918f; font-weight: 600; text-transform: uppercase; margin: 10px 10px; }
        .history-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }
        .history-item { padding: 10px 12px; border-radius: 12px; font-size: 0.85rem; color: #c4c7c5; cursor: pointer; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .history-item:hover, .history-item.active { background-color: #282a2c; color: #fff; }

        /* Zone Principale de Chat */
        .main-chat { flex: 1; display: flex; flex-direction: column; height: 100vh; }
        .header { padding: 15px 20px; border-bottom: 1px solid #2d2f31; display: flex; align-items: center; gap: 15px; }
        .toggle-sidebar-btn { background: none; border: none; color: #e3e3e3; cursor: pointer; font-size: 1.2rem; }
        .header h2 { font-size: 1.1rem; font-weight: 500; color: #a8c7fa; }

        .messages-container { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }
        .message-row { display: flex; gap: 12px; max-width: 80%; }
        .message-row.user { align-self: flex-end; flex-direction: row-reverse; }
        .message-row.bot { align-self: flex-start; }
        .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; font-size: 0.85rem; }
        .user .avatar { background: #004a77; color: #c2e7ff; }
        .bot .avatar { background: linear-gradient(135deg, #a8c7fa, #669df6); color: #040c19; }
        .bubble { padding: 14px 18px; border-radius: 20px; line-height: 1.5; font-size: 0.95rem; white-space: pre-wrap; word-break: break-word; }
        .user .bubble { background: #283445; border-top-right-radius: 4px; }
        .bot .bubble { background: #27292a; border-top-left-radius: 4px; }

        /* Zone de Saisie */
        .input-area { padding: 15px 20px 25px 20px; }
        .input-wrapper { max-width: 800px; margin: 0 auto; background-color: #282a2c; border-radius: 28px; display: flex; align-items: center; padding: 6px 10px 6px 20px; }
        input[type="text"] { flex: 1; background: transparent; border: none; outline: none; color: #fff; font-size: 1rem; }
        .send-btn { background: linear-gradient(135deg, #a8c7fa, #669df6); border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .send-btn svg { fill: #040c19; width: 18px; height: 18px; }
    </style>
</head>
<body>
    <div class="sidebar" id="sidebar">
        <button class="new-chat-btn" onclick="createNewChat()">
            <span>+</span> Nouvelle discussion
        </button>
        <div class="history-title">Discussions récentes</div>
        <div class="history-list" id="historyList"></div>
    </div>

    <div class="main-chat">
        <div class="header">
            <button class="toggle-sidebar-btn" onclick="toggleSidebar()">☰</button>
            <h2>Pig🐷 - Professeur de Code</h2>
        </div>

        <div class="messages-container" id="messages">
            <div class="message-row bot">
                <div class="avatar">🐷</div>
                <div class="bubble">Bonjour ! Je suis <b>Pig🐷</b>. Pose-moi une question sur le code ou demande une leçon !</div>
            </div>
        </div>

        <div class="input-area">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Pose une question à Lou Tsanta..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">
                    <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = localStorage.getItem('current_session') || createNewSessionId();
        let chatsHistory = JSON.parse(localStorage.getItem('chats_history') || '{}');

        function createNewSessionId() {
            const newId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('current_session', newId);
            return newId;
        }

        function createNewChat() {
            currentSessionId = createNewSessionId();
            document.getElementById('messages').innerHTML = `
                <div class="message-row bot">
                    <div class="avatar">🐷</div>
                    <div class="bubble">Nouvelle discussion démarrée ! Quel sujet souhaites-tu aborder ?</div>
                </div>
            `;
            renderHistory();
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.style.display = sidebar.style.display === 'none' ? 'flex' : 'none';
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            Object.keys(chatsHistory).reverse().forEach(id => {
                const item = document.createElement('div');
                item.className = `history-item ${id === currentSessionId ? 'active' : ''}`;
                item.textContent = chatsHistory[id].title || 'Discussion';
                item.onclick = () => loadChat(id);
                list.appendChild(item);
            });
        }

        function loadChat(id) {
            currentSessionId = id;
            localStorage.setItem('current_session', id);
            const chat = chatsHistory[id];
            const container = document.getElementById('messages');
            container.innerHTML = '';
            
            chat.messages.forEach(msg => {
                const row = document.createElement('div');
                row.className = `message-row ${msg.sender}`;
                row.innerHTML = `<div class="avatar">${msg.sender === 'user' ? 'T' : 'L'}</div><div class="bubble">${escapeHtml(msg.text)}</div>`;
                container.appendChild(row);
            });
            renderHistory();
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const messages = document.getElementById('messages');
            const text = input.value.trim();
            if (!text) return;

            // Sauvegarde dans l'historique local du titre
            if (!chatsHistory[currentSessionId]) {
                chatsHistory[currentSessionId] = { title: text.substring(0, 25) + '...', messages: [] };
            }

            // Ajout message utilisateur
            appendMessage('user', text);
            chatsHistory[currentSessionId].messages.push({ sender: 'user', text: text });
            localStorage.setItem('chats_history', JSON.stringify(chatsHistory));

            input.value = '';

            // Bulle temporaire d'attente
            const botRow = document.createElement('div');
            botRow.className = 'message-row bot';
            botRow.innerHTML = `<div class="avatar">L</div><div class="bubble">Lou Tsanta réfléchit...</div>`;
            messages.appendChild(botRow);
            messages.scrollTop = messages.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, session_id: currentSessionId })
                });
                const data = await res.json();
                
                const replyText = data.response || ('Erreur : ' + (data.error || 'Problème de réponse'));
                botRow.querySelector('.bubble').textContent = replyText;
                
                chatsHistory[currentSessionId].messages.push({ sender: 'bot', text: replyText });
                localStorage.setItem('chats_history', JSON.stringify(chatsHistory));
            } catch (err) {
                botRow.querySelector('.bubble').textContent = 'Erreur de connexion.';
            }
            renderHistory();
            messages.scrollTop = messages.scrollHeight;
        }

        function appendMessage(sender, text) {
            const messages = document.getElementById('messages');
            const row = document.createElement('div');
            row.className = `message-row ${sender}`;
            row.innerHTML = `<div class="avatar">${sender === 'user' ? 'T' : 'L'}</div><div class="bubble">${escapeHtml(text)}</div>`;
            messages.appendChild(row);
            messages.scrollTop = messages.scrollHeight;
        }

        function escapeHtml(str) {
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        // Chargement initial
        renderHistory();
        if (chatsHistory[currentSessionId]) loadChat(currentSessionId);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default_session')

    if not user_message:
        return jsonify({'error': 'Message vide'}), 400

    try:
        reply = get_gemini_reply(session_id, user_message)
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
