from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Infini</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        html, body {
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: #18191a;
            color: #e4e6eb;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        .messenger-container {
            display: flex;
            flex-direction: column;
            height: 100%;
            max-width: 480px;
            margin: 0 auto;
            background-color: #242526;
        }

        .messenger-header {
            flex-shrink: 0;
            background-color: #242526;
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #393a3b;
        }
        .header-title {
            font-weight: bold;
            font-size: 0.95em;
            color: #e4e6eb;
        }
        .reset-btn {
            background: #3a3b3c;
            color: #b0b3b8;
            border: none;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            text-decoration: none;
            cursor: pointer;
        }
        .reset-btn:hover { background: #4e4f50; }

        .messenger-form {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
        }

        .top-panel {
            flex-shrink: 0;
            background-color: #242526;
            padding: 6px 10px;
            border-bottom: 1px solid #393a3b;
            font-size: 0.75em;
        }
        .config-row {
            display: flex;
            gap: 4px;
            margin-bottom: 4px;
        }
        input[type="text"] {
            flex: 1;
            background-color: #3a3b3c;
            border: 1px solid #393a3b;
            color: #e4e6eb;
            padding: 6px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #0084ff;
        }
        .scores-text {
            color: #0084ff;
            font-weight: bold;
            text-align: center;
            font-size: 0.8em;
            margin-top: 2px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background-color: #242526;
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-height: 0;
        }
        .msg-row {
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }
        .avatar-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #3a3b3c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1em;
            flex-shrink: 0;
            border: 1px solid #4e4f50;
        }
        .msg-content {
            max-width: 75%;
            display: flex;
            flex-direction: column;
        }
        .msg-bubble {
            background-color: #3a3b3c;
            color: #e4e6eb;
            padding: 8px 12px;
            border-radius: 16px;
            font-size: 0.85em;
            word-wrap: break-word;
            position: relative;
        }
        .msg-sender {
            font-size: 0.7em;
            color: #b0b3b8;
            margin-bottom: 2px;
            margin-left: 4px;
        }
        .judge-info {
            font-size: 0.7em;
            color: #9cb4cc;
            margin-top: 3px;
            font-style: italic;
            border-top: 1px dashed rgba(255,255,255,0.1);
            padding-top: 2px;
        }
        .delete-link {
            color: #ff5252;
            font-size: 0.75em;
            text-decoration: none;
            float: right;
            margin-left: 6px;
            font-weight: bold;
        }

        .messenger-input-area {
            flex-shrink: 0;
            background-color: #242526;
            padding: 10px 12px;
            border-top: 1px solid #393a3b;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .message-input {
            flex: 1;
            background-color: #3a3b3c;
            border: none;
            color: #e4e6eb;
            padding: 10px 14px;
            border-radius: 20px;
            font-size: 0.95em;
            outline: none;
        }
        .message-input::placeholder {
            color: #b0b3b8;
        }
        .send-btn {
            background-color: #0084ff;
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.1em;
            flex-shrink: 0;
        }
        .send-btn:active {
            transform: scale(0.92);
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💬 Chrono-Royaume Infini</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <input type="text" name="username" placeholder="Votre Nom (ex: Tsanta)" value="Tsanta" required>
                <input type="text" name="role" placeholder="Personnage / Rôle libre (ex: Elfe, Mage...)" value="Sorcier" required>
            </div>
            <div class="config-row">
                <input type="text" name="scenario" placeholder="Situation / Scénario libre (ex: Dans le futur...)" value="Le Royaume Effondré" required>
            </div>
            <div class="scores-text">
                {% if scores %}
                    {% for user, pts in scores.items() %}
                        {{ user }}: {{ pts }} pts &nbsp;&nbsp;
                    {% endfor %}
                {% else %}
                    Scores: 0 pts
                {% endif %}
            </div>
        </div>

        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            {{ m.text }}
                            <div class="judge-info">🌐 [{{ m.scenario }}] ⚖️ {{ m.comment }} (+{{ m.points }}pts)</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa Message..." required autocomplete="off">
            <button type="submit" class="send-btn" title="Envoyer">➤</button>
        </div>
    </form>
</div>

<script>
    const cb = document.getElementById('chatbox');
    if(cb) { cb.scrollTop = cb.scrollHeight; }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, messages=game_state["messages"], scores=game_state["scores"])

@app.route('/send', methods=['POST'])
def send():
    sender = request.form.get('username', 'Anonyme').strip() or 'Anonyme'
    role = request.form.get('role', 'Personnage').strip() or 'Personnage'
    scenario = request.form.get('scenario', 'Libre').strip() or 'Libre'
    text = request.form.get('text', '').strip()
    
    if text:
        # Génération automatique d'un avatar basé sur le texte du rôle ou aléatoire si inconnu
        emojis = ["🧙‍♂️", "✨", "🗡️", "👑", "⏳", "🐉", "🔮", "🧝‍♀️", "🥷", "🧛‍♂️", "🤖", "🦊", "🌟", "🛡️"]
        avatar = random.choice(emojis)

        points = 10
        comment = f"Réplique validée dans '{scenario}' !"
        if any(w in text.lower() for w in ['amour', 't’aime', 'coeur', 'tiako', 'mandrasa']):
            points = 20
            comment = "Coup de cœur romantique absolu dans le temps !"

        if sender not in game_state["scores"]:
            game_state["scores"][sender] = 100
        game_state["scores"][sender] += points
        
        game_state["messages"].append({
            "sender": sender,
            "role": role,
            "scenario": scenario,
            "avatar": avatar,
            "text": text,
            "comment": comment,
            "points": points
        })
        
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_msg(index):
    if 0 <= index < len(game_state["messages"]):
        game_state["messages"].pop(index)
    return redirect(url_for('index'))

@app.route('/reset')
def reset_data():
    game_state["messages"] = []
    game_state["scores"] = {}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)