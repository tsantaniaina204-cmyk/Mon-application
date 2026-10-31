from flask import Flask, render_template_string, request, redirect, url_for

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chrono-Royaume - Messenger</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #18191a;
            color: #e4e6eb;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        .messenger-container {
            width: 100%;
            max-width: 480px;
            height: 100vh;
            background-color: #242526;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        @media (min-height: 650px) {
            .messenger-container {
                height: 94vh;
                border-radius: 12px;
                overflow: hidden;
            }
        }
        
        /* En-tête Messenger ultra compact */
        .messenger-header {
            background-color: #242526;
            padding: 8px 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #393a3b;
            flex-shrink: 0;
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

        /* Panneau supérieur très compact sur une seule ligne ou réduit */
        .top-panel {
            background-color: #242526;
            padding: 6px 10px;
            border-bottom: 1px solid #393a3b;
            font-size: 0.75em;
            flex-shrink: 0;
        }
        .config-row {
            display: flex;
            gap: 4px;
            margin-bottom: 4px;
        }
        select, input[type="text"] {
            flex: 1;
            background-color: #3a3b3c;
            border: 1px solid #393a3b;
            color: #e4e6eb;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            outline: none;
        }
        select:focus, input[type="text"]:focus {
            border-color: #0084ff;
        }
        .scores-text {
            color: #0084ff;
            font-weight: bold;
            text-align: center;
            font-size: 0.8em;
        }

        /* Zone de messages qui prend toute la place centrale */
        .chat-messages {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
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

        /* Barre de saisie Messenger TOUJOURS visible en bas */
        .messenger-input-area {
            background-color: #242526;
            padding: 8px 10px;
            border-top: 1px solid #393a3b;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }
        .message-input {
            flex: 1;
            background-color: #3a3b3c;
            border: none;
            color: #e4e6eb;
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 0.9em;
            outline: none;
        }
        .message-input::placeholder {
            color: #b0b3b8;
        }
        .send-btn {
            background-color: #0084ff;
            color: white;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1em;
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
        <div class="header-title">💬 Chrono-Royaume</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <input type="text" name="username" placeholder="Votre Nom" value="Tsanta" required>
                <select name="role">
                    <option value="Sorcier">🧙‍♂️ Sorcier</option>
                    <option value="Magicien">✨ Magicien</option>
                    <option value="Guerrier">🗡️ Guerrier</option>
                    <option value="Roi/Reine">👑 Roi / Reine</option>
                    <option value="Voyageur">⏳ Voyageur</option>
                </select>
            </div>
            <div class="config-row">
                <select name="scenario">
                    <option value="Royaume Effondré">🏰 Scénario : Royaume Effondré</option>
                    <option value="Faille Temporelle">⚡ Scénario : Faille Temporelle</option>
                </select>
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

        <!-- Zone de messages -->
        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            {{ m.text }}
                            <div class="judge-info">⚖️ {{ m.comment }} (+{{ m.points }}pts)</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <!-- Boîte d'envoi Messenger fixée en bas -->
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
    role = request.form.get('role', 'Sorcier')
    scenario = request.form.get('scenario', 'Général')
    text = request.form.get('text', '').strip()
    
    if text:
        role_avatars = {
            "Sorcier": "🧙‍♂️",
            "Magicien": "✨",
            "Guerrier": "🗡️",
            "Roi/Reine": "👑",
            "Voyageur": "⏳"
        }
        avatar = role_avatars.get(role, "💬")

        points = 10
        comment = "Réplique validée par le juge !"
        if 'amour' in text.lower() or 't’aime' in text.lower() or 'coeur' in text.lower():
            points = 20
            comment = "Coup de cœur romantique absolu !"

        if sender not in game_state["scores"]:
            game_state["scores"][sender] = 100
        game_state["scores"][sender] += points
        
        game_state["messages"].append({
            "sender": sender,
            "role": role,
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