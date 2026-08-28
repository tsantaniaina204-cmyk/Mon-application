import os
from flask import Flask, render_template_string, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Tes clés API découpées
KEYS_GROUP_1 = [
    "AQ.Ab8RN6Jh6poXd" + "Q6zBqLXq-cco-WWA00Qotygr3_W10SFZOxVuA",
    "AQ.Ab8RN6KYOMekMj" + "9RLFEWOozlhQ1GMirPoqkSwkA_BH_zl_3XDg",
    "AQ.Ab8RN6Lu7uH66i" + "E1DIyUGHobdjfSaygqyvQKQJvia6JKLXbsAQ"
]

KEYS_GROUP_2 = [
    "AQ.Ab8RN6K9wK1Ht8" + "p_eA2ExjYLFqEstXH0wLKMrLAci_NLcTgiHQ",
    "AQ.Ab8RN6IIRRims_" + "MR2hnVWBbLc9PNqLUpe-8uOTL-pkC2x8eUZg"
]

API_KEYS = KEYS_GROUP_1 + KEYS_GROUP_2

SYSTEM_INSTRUCTION = """
Tu es un expert mondial de haut niveau en Mathématiques et en Programmation.
Consignes d'affichage impératives :
1. Pour TOUT résultat ou formule mathématique importante, entoure-le de LaTeX en utilisant des blocs de couleur RGB comme ceci : `\\color{rgb}{0.1, 0.7, 0.3}{ton_equation_ici}`.
2. Tout code informatique DOIT être placé exclusivement dans des blocs Markdown standard avec le nom du langage (ex: ```python ... ```).
3. Ne mets AUCUNE salutation, introduction ou explication avant le bloc de code si la demande concerne uniquement l'écriture d'un script.
"""

def generate_response(prompt_text):
    """
    Utilise le nouveau SDK `google-genai` pour générer une réponse.
    """
    for key in API_KEYS:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            if response and response.text:
                return response.text
        except Exception:
            # Si un modèle ou une clé échoue, essaie avec gemini-2.0-flash
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue
            
    return "❌ Impossible de contacter l'API. Vérifiez la validité de vos clés."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pigmini AI</title>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #f8fa221a; color: #1f1f1f; display: flex; flex-direction: column; height: 100vh; background: linear-gradient(180deg, #eef4ff 0%, #ffffff 100%); }
        header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; font-size: 20px; font-weight: 600; }
        .icon-btn { background: none; border: none; font-size: 24px; cursor: pointer; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .welcome { text-align: center; margin-top: auto; margin-bottom: auto; }
        .welcome .logo { font-size: 64px; margin-bottom: 10px; }
        .welcome h1 { font-size: 36px; color: #444746; font-weight: 400; }
        .messages-list { width: 100%; max-width: 800px; display: flex; flex-direction: column; gap: 20px; }
        .message-row { display: flex; gap: 12px; width: 100%; }
        .message-row.user { justify-content: flex-end; }
        .avatar { font-size: 24px; min-width: 32px; text-align: center; }
        .bubble { max-width: 85%; padding: 14px 18px; border-radius: 18px; font-size: 16px; line-height: 1.5; word-break: break-word; }
        .user .bubble { background-color: #e3eddfff; color: #041e49; border-top-right-radius: 4px; }
        .ai .bubble { background-color: #ffffff; border: 1px solid #e3e3e3; border-top-left-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
        .code-block-container { position: relative; margin: 12px 0; border-radius: 8px; overflow: hidden; background: #2d2d2d; }
        .code-header { display: flex; justify-content: space-between; align-items: center; background: #1e1e1e; padding: 6px 12px; color: #d4d4d4; font-size: 12px; }
        .copy-btn { background: #3a3a3a; border: none; color: #fff; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .copy-btn:hover { background: #555; }
        pre { margin: 0 !important; padding: 12px !important; overflow-x: auto; }
        .input-area { width: 100%; display: flex; justify-content: center; padding: 20px; }
        .input-box { width: 100%; max-width: 800px; background: #ffffff; border-radius: 30px; display: flex; align-items: center; padding: 8px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e0e0e0; }
        .input-box input { flex: 1; border: none; outline: none; padding: 12px; font-size: 16px; background: transparent; }
        .send-btn { background: #1a73e8; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; justify-content: center; align-items: center; }
    </style>
</head>
<body>
    <header>
        <div>☰ &nbsp; 🐷 Pigmini <span style="font-size:14px; color:#666;">Flash</span></div>
        <div><button class="icon-btn" onclick="resetChat()" title="Nouvelle discussion">✏️</button></div>
    </header>
    <div id="chat-container">
        <div id="welcome-screen" class="welcome">
            <div class="logo">🐷</div>
            <h1>Par où commencer ?</h1>
        </div>
        <div class="messages-list" id="messages-list"></div>
    </div>
    <div class="input-area">
        <div class="input-box">
            <button class="icon-btn">+</button>
            <input type="text" id="user-input" placeholder="Demander à Pigmini..." onkeydown="if(event.key === 'Enter') sendMessage()">
            <button class="send-btn" onclick="sendMessage()">➔</button>
        </div>
    </div>
    <script>
        function resetChat() {
            document.getElementById('messages-list').innerHTML = '';
            document.getElementById('welcome-screen').style.display = 'block';
        }
        async function sendMessage() {
            const inputEl = document.getElementById('user-input');
            const text = inputEl.value.trim();
            if (!text) return;
            document.getElementById('welcome-screen').style.display = 'none';
            inputEl.value = '';
            const list = document.getElementById('messages-list');
            list.innerHTML += `<div class="message-row user"><div class="bubble">${escapeHtml(text)}</div><div class="avatar">🐱</div></div>`;
            const aiMsgId = 'ai-' + Date.now();
            list.innerHTML += `<div class="message-row ai"><div class="avatar">🐷</div><div class="bubble" id="${aiMsgId}"><i>Traitement en cours...</i></div></div>`;
            const chatContainer = document.getElementById('chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                const aiBubble = document.getElementById(aiMsgId);
                aiBubble.innerHTML = parseResponse(data.reply);
                Prism.highlightAllUnder(aiBubble);
                if (window.MathJax) { MathJax.typesetPromise([aiBubble]); }
            } catch (err) {
                document.getElementById(aiMsgId).innerText = "Erreur de connexion avec le serveur.";
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        function escapeHtml(str) { return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        function parseResponse(text) {
            const codeBlockRegex = /```(\\w*)\\n([\\s\\S]*?)```/g;
            let formatted = text.replace(codeBlockRegex, (match, lang, code) => {
                const cleanCode = escapeHtml(code.trim());
                const languageClass = lang ? `language-${lang}` : 'language-plaintext';
                return `<div class="code-block-container"><div class="code-header"><span>${lang || 'Code'}</span><button class="copy-btn" onclick="copyCode(this)">Copier le code</button></div><pre><code class="${languageClass}">${cleanCode}</code></pre></div>`;
            });
            return formatted.replace(/\\n/g, '<br>');
        }
        function copyCode(button) {
            const codeEl = button.closest('.code-block-container').querySelector('code');
            navigator.clipboard.writeText(codeEl.innerText).then(() => {
                button.innerText = 'Copié !';
                setTimeout(() => button.innerText = 'Copier le code', 2000);
            });
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
    reply_text = generate_response(user_message)
    return jsonify({'reply': reply_text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
