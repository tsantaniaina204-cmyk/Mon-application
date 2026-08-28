from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# Masquage et assemblage des clés en deux blocs (Groupe 1)
API_KEYS_GROUP_1 = [
    "AQ.Ab8RN6Jh6poXdQ" + "6zBqLXq-cco-WWA00Qotygr3_W10SFZOxVuA",
    "AQ.Ab8RN6KYOMekMj" + "9RLFEWOozlhQ1GMirPoqkSwkA_BH_zl_3XDg",
    "AQ.Ab8RN6Lu7uH66i" + "E1DIyUGHobdjfSaygqyvQKQJvia6JKLXbsAQ"
]

# Masquage et assemblage des clés en deux blocs (Groupe 2)
API_KEYS_GROUP_2 = [
    "AQ.Ab8RN6K9wK1Ht8" + "p_eA2ExjYLFqEstXH0wLKMrLAci_NLcTgiHQ",
    "AQ.Ab8RN6IIRRims_" + "MR2hnVWBbLc9PNqLUpe-8uOTL-pkC2x8eUZg"
]

# Configuration du rôle pédagogique
SYSTEM_INSTRUCTION = """
Tu es "Pig🐷", un assistant virtuel expert et un excellent professeur de programmation.
Ton rôle est de donner des leçons de programmation claires, progressives et adaptées à l'utilisateur.
- Explique les concepts étape par étape avec des exemples de code concrets.
- Sois encourageant, pédagogique et structuré.
- Couvre des sujets comme Python, PHP, C++, JavaScript, HTML/CSS, etc.
- Quand l'utilisateur pose une question, réponds en expliquant d'abord la théorie simplement, puis donne un exemple pratique.
Ton unique créateur est FIDIMANANTSOA Tsantaniaina, c'est un jeune homme, tu lui doit de réspect
Utilise des émojies à chaque réponses, surtout cette émoji: '🐷' 

"""

def generate_with_fallback(prompt):
    """Bascule d'une clé à l'autre entre le Groupe 1 et le Groupe 2 en cas de limite de quota."""
    groups = [API_KEYS_GROUP_1, API_KEYS_GROUP_2]
    last_error = None

    for group_index, group in enumerate(groups, start=1):
        for key in group:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                return response.text
            except Exception as e:
                last_error = e
                continue

    raise Exception(f"Erreur lors de la génération : {last_error}")

# HTML/CSS avec design moderne aux formes très arrondies
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lou Tsanta - IA</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: #131314;
            color: #e3e3e3;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            padding: 10px;
        }

        .chat-container {
            width: 100%;
            max-width: 850px;
            height: 92vh;
            background-color: #1e1f20;
            border-radius: 28px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }

        .chat-header {
            padding: 20px 24px;
            background-color: #1e1f20;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #2d2f31;
        }

        .avatar-header {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #a8c7fa, #669df6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #040c19;
            font-weight: bold;
            font-size: 1.1rem;
        }

        .chat-header h2 {
            font-size: 1.15rem;
            font-weight: 500;
            color: #e3e3e3;
        }

        .chat-messages {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .message-row {
            display: flex;
            gap: 12px;
            max-width: 85%;
        }

        .message-row.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .message-row.bot {
            align-self: flex-start;
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: bold;
            flex-shrink: 0;
        }

        .user .avatar {
            background-color: #004a77;
            color: #c2e7ff;
        }

        .bot .avatar {
            background: linear-gradient(135deg, #a8c7fa, #669df6);
            color: #040c19;
        }

        .bubble {
            padding: 14px 20px;
            border-radius: 22px;
            line-height: 1.5;
            font-size: 0.95rem;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .user .bubble {
            background-color: #283445;
            color: #e3e3e3;
            border-top-right-radius: 6px;
        }

        .bot .bubble {
            background-color: #27292a;
            color: #e3e3e3;
            border-top-left-radius: 6px;
        }

        .chat-input-area {
            padding: 16px 24px 24px 24px;
            background-color: #1e1f20;
        }

        .input-wrapper {
            background-color: #282a2c;
            border-radius: 30px;
            display: flex;
            align-items: center;
            padding: 6px 8px 6px 20px;
            transition: background-color 0.2s;
        }

        .input-wrapper:focus-within {
            background-color: #313335;
        }

        input[type="text"] {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #e3e3e3;
            font-size: 1rem;
            padding: 10px 0;
        }

        input[type="text"]::placeholder {
            color: #8e918f;
        }

        button {
            background: linear-gradient(135deg, #a8c7fa, #669df6);
            border: none;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.1s;
        }

        button:active {
            transform: scale(0.95);
        }

        button svg {
            fill: #040c19;
            width: 20px;
            height: 20px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="avatar-header">🐷</div>
            <h2>Pig🐷</h2>
        </div>

        <div class="chat-messages" id="messages">
            <div class="message-row bot">
                <div class="avatar">🐷</div>
                <div class="bubble">Bonjour ! Je suis <b>Pig🐷</b>. Pose-moi tes questions sur la programmation ou demande-moi une leçon !</div>
            </div>
        </div>

        <div class="chat-input-area">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Pose une question à Lou Tsanta..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()">
                    <svg viewBox="0 0 24 24">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const messages = document.getElementById('messages');
            const text = input.value.trim();
            if (!text) return;

            // Ajout du message utilisateur
            const userRow = document.createElement('div');
            userRow.className = 'message-row user';
            userRow.innerHTML = `
                <div class="avatar">🐭</div>
                <div class="bubble">${escapeHtml(text)}</div>
            `;
            messages.appendChild(userRow);

            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // Bulle temporaire pendant le chargement
            const botRow = document.createElement('div');
            botRow.className = 'message-row bot';
            botRow.innerHTML = `
                <div class="avatar">🐷</div>
                <div class="bubble">En train de réfléchir...</div>
            `;
            messages.appendChild(botRow);
            messages.scrollTop = messages.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                botRow.querySelector('.bubble').textContent = data.response || ('Erreur : ' + (data.error || 'Une erreur est survenue.'));
            } catch (err) {
                botRow.querySelector('.bubble').textContent = 'Erreur de connexion avec le serveur.';
            }
            messages.scrollTop = messages.scrollHeight;
        }

        function escapeHtml(str) {
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400

    try:
        reply = generate_with_fallback(user_message)
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
