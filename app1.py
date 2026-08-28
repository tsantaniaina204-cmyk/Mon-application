from flask import Flask, request, jsonify, render_template_string
from google import genai
from google.genai import types

app = Flask(__name__)

# Assemblage des clés du Groupe 1 (Partie A + Partie B)
API_KEYS_GROUP_1 = [
    "AQ.Ab8RN6Jh6poXdQ" + "6zBqLXq-cco-WWA00Qotygr3_W10SFZOxVuA",
    "AQ.Ab8RN6KYOMekMj" + "9RLFEWOozlhQ1GMirPoqkSwkA_BH_zl_3XDg",
    "AQ.Ab8RN6Lu7uH66i" + "E1DIyUGHobdjfSaygqyvQKQJvia6JKLXbsAQ"
]

# Assemblage des clés du Groupe 2 (Partie A + Partie B)
API_KEYS_GROUP_2 = [
    "AQ.Ab8RN6K9wK1Ht8" + "p_eA2ExjYLFqEstXH0wLKMrLAci_NLcTgiHQ",
    "AQ.Ab8RN6IIRRims_" + "MR2hnVWBbLc9PNqLUpe-8uOTL-pkC2x8eUZg"
]

SYSTEM_INSTRUCTION = """
Tu es "Lou Tsanta", un assistant virtuel expert et un excellent professeur de programmation.
Ton rôle est de donner des leçons de programmation claires, progressives et adaptées à l'utilisateur.
- Explique les concepts étape par étape avec des exemples de code concrets.
- Sois encourageant, pédagogique et structuré.
- Couvre des sujets comme Python, PHP, C++, JavaScript, HTML/CSS, etc.
- Quand l'utilisateur pose une question, réponds en expliquant d'abord la théorie simplement, puis donne un exemple pratique.
- Tu es fort en hacking
"""

def generate_with_fallback(prompt):
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

    raise Exception(f"Erreur de génération : {last_error}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lou Tsanta - Prof de Code</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { background-color: #12181b; color: #e0e0e0; margin: 0; padding: 20px; }
        .chat-container { max-width: 700px; margin: 20px auto; background: #1e272c; border-radius: 12px; display: flex; flex-direction: column; height: 85vh; }
        .chat-header { background: #2a373e; padding: 15px 20px; border-top-left-radius: 12px; border-top-right-radius: 12px; border-bottom: 1px solid #37474f; }
        .chat-header h2 { margin: 0; color: #00bfa5; font-size: 1.2rem; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { padding: 12px 16px; border-radius: 8px; max-width: 85%; line-height: 1.5; white-space: pre-wrap; }
        .user-message { background: #004d40; color: #e0f2f1; align-self: flex-end; }
        .bot-message { background: #263238; color: #eceff1; align-self: flex-start; border-left: 4px solid #00bfa5; }
        .chat-input { padding: 15px; background: #2a373e; display: flex; gap: 10px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }
        input[type="text"] { flex: 1; padding: 12px; background: #12181b; border: 1px solid #37474f; color: #fff; border-radius: 6px; outline: none; }
        button { padding: 12px 20px; background: #00bfa5; border: none; color: #12181b; font-weight: bold; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>Lou Tsanta - Professeur de Programmation</h2>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot-message">Bonjour ! Je suis <b>Lou Tsanta</b>. Pose-moi une question ou demande une leçon de code !</div>
        </div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Pose ta question ici..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Envoyer</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const messages = document.getElementById('messages');
            const text = input.value.trim();
            if (!text) return;

            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.textContent = text;
            messages.appendChild(userDiv);

            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            const botDiv = document.createElement('div');
            botDiv.className = 'message bot-message';
            botDiv.textContent = 'Lou Tsanta prépare la réponse...';
            messages.appendChild(botDiv);
            messages.scrollTop = messages.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                botDiv.textContent = data.response || ('Erreur : ' + (data.error || 'Erreur inconnue'));
            } catch (err) {
                botDiv.textContent = 'Erreur de connexion.';
            }
            messages.scrollTop = messages.scrollHeight;
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
