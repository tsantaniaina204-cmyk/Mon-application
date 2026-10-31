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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume Magique 🔮</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        html, body {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
            display: flex; justify-content: center; align-items: center;
        }

        .chat-container {
            width: 100%; max-width: 450px; height: 100%;
            background: #ffffff; display: flex; flex-direction: column;
            position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        @media (min-height: 600px) and (min-width: 460px) {
            .chat-container { height: 92%; border-radius: 16px; overflow: hidden; }
        }

        .chat-header {
            background: #0f4c81; color: white; padding: 10px 12px;
            text-align: center; font-weight: bold; font-size: 1em;
            display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;
        }
        .header-btn {
            background: rgba(255,255,255,0.2); color: white; border: none;
            padding: 3px 8px; border-radius: 10px; font-size: 0.7em; cursor: pointer; text-decoration: none;
        }
        .scores-board {
            display: flex; justify-content: space-around; background: #e8f4f8;
            padding: 6px; font-weight: bold; color: #1f4068; font-size: 0.75em;
            border-bottom: 1px solid #d1e8e2; flex-shrink: 0; overflow-x: auto;
        }
        .config-bar {
            padding: 6px 8px; background: #f4f4f4; border-bottom: 1px solid #ddd;
            display: flex; flex-direction: column; gap: 4px; flex-shrink: 0;
        }
        .config-row { display: flex; gap: 4px; }
        select, input {
            flex: 1; padding: 6px; border-radius: 5px;
            border: 1px solid #ccc; font-size: 0.75em; background: #fff;
            outline: none;
        }

        .chat-messages {
            flex: 1; padding: 10px; overflow-y: auto; background: #f7f9fb;
            display: flex; flex-direction: column; gap: 8px;
            -webkit-overflow-scrolling: touch;
        }
        
        .msg-wrapper { 
            display: flex; align-items: flex-start; gap: 6px; 
        }

        .avatar-box {
            width: 32px; height: 32px; border-radius: 50%;
            background: #e4e4e4; display: flex; align-items: center; justify-content: center;
            font-size: 1.1em; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex-shrink: 0;
            border: 2px solid #0f4c81;
        }
        .msg-bubble {
            max-width: 75%; padding: 8px 10px; border-radius: 10px;
            font-size: 0.8em; position: relative; background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e1e1e1;
            word-wrap: break-word;
        }
        .msg-header-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
        .msg-sender { font-weight: bold; color: #0f4c81; font-size: 0.8em; }
        .delete-btn {
            background: none; border: none; color: #ff6b6b; cursor: pointer;
            font-size: 0.8em; padding: 0 4px; text-decoration: none;
        }
        .power-tag {
            font-size: 0.65em; background: #fff3cd; color: #856404;
            padding: 1px 5px; border-radius: 3px; margin-bottom: 3px; display: inline-block;
            font-weight: bold;
        }
        .judge-note {
            font-size: 0.7em; margin-top: 4px; font-style: italic; color: #555;
            border-top: 1px dashed #eee; padding-top: 2px;
        }

        .chat-input-area {
            padding: 8px; background: #fff; border-top: 1px solid #ddd;
            display: flex; gap: 6px; flex-shrink: 0; align-items: center;
        }
        .chat-input-area input {
            padding: 8px; font-size: 0.85em; border-radius: 18px;
        }
        .send-btn {
            background: #0f4c81; color: white; border: none; padding: 0 14px;
            height: 34px; border-radius: 18px; font-weight: bold; cursor: pointer; font-size: 0.8em;
            flex-shrink: 0;
        }
        .send-btn:active { transform: scale(0.92); }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <span>⏳ Chrono-Royaume Magique 🔮</span>
        <a href="/reset" class="header-btn">🔄 Reset</a>
    </div>

    <div class="scores-board" id="scores-board">
        {% if scores %}
            {% for user, pts in scores.items() %}
                <span>{{ user }}: {{ pts }} pts</span>
            {% endfor %}
        {% else %}
            <span>Aucun score pour l'instant</span>
        {% endif %}
    </div>

    <!-- FORMULAIRE PRINCIPAL -->
    <form action="/send" method="POST" class="config-bar" style="border:none; padding:6px 8px;">
        <div class="config-row">
            <input type="text" name="username" placeholder="Ton Prénom" value="Tsanta">
            <select name="role">
                <option value="Sorcier">🔮 Sorcier (Ombre)</option>
                <option value="Magicien">✨ Magicien (Stellaire)</option>
                <option value="Guerrier">🗡️ Guerrier (Feu)</option>
                <option value="Mage">📜 Mage (Ancien)</option>
                <option value="Roi/Reine">👑 Roi/Reine (Royal)</option>
                <option value="Voyageur">⏳ Voyageur (Temporel)</option>
            </select>
        </div>
        <div class="config-row" style="margin-top:4px;">
            <select name="scenario">
                <option value="Le Royaume Effondré">🏰 Scénario : Royaume Effondré</option>
                <option value="La Faille Temporelle">⚡ Scénario : Faille Temporelle</option>
                <option value="Le Labyrinthe des Âmes">🌀 Scénario : Labyrinthe des Âmes</option>
                <option value="L'Ère des Dragons">🐉 Scénario : Ère des Dragons</option>
            </select>
        </div>

        <div class="chat-messages" id="chat-box" style="margin-top:6px; height:180px;">
            {% for m in messages %}
                <div class="msg-wrapper">
                    <div class="avatar-box">{{ m.avatar }}</div>
                    <div class="msg-bubble">
                        <div class="msg-header-info">
                            <span class="msg-sender">{{ m.sender }} ({{ m.role }})</span>
                            <a href="/delete/{{ loop.index0 }}" class="delete-btn" title="Supprimer">❌</a>
                        </div>
                        <div class="power-tag">⚡ {{ m.power }}</div>
                        <div>{{ m.text }}</div>
                        <div class="judge-note">⚖️ {{ m.comment }} (+{{ m.points }} pts)</div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="chat-input-area" style="border:none; padding:4px 0 0 0; background:transparent;">
            <input type="text" name="text" placeholder="Invoque ta réplique..." required autocomplete="off">
            <button type="submit" class="send-btn">Lancer</button>
        </div>
    </form>
</div>

<script>
    // Fait défiler automatiquement vers le bas des messages à l'ouverture
    const box = document.getElementById('chat-box');
    if(box) { box.scrollTop = box.scrollHeight; }
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
        role_config = {
            "Sorcier": {"avatar": "🧙‍♂️", "power": "Magie Noire & Illusions"},
            "Magicien": {"avatar": "✨", "power": "Sortilèges Stellaires"},
            "Guerrier": {"avatar": "🗡️", "power": "Frappe de Feu Sacré"},
            "Mage": {"avatar": "📜", "power": "Anciennes Connaissances"},
            "Roi/Reine": {"avatar": "👑", "power": "Décret Royal Absolu"},
            "Voyageur": {"avatar": "⏳", "power": "Manipulation du Temps"}
        }
        
        config = role_config.get(role, {"avatar": "🔮", "power": "Mystère Pur"})
        avatar = config["avatar"]
        power = config["power"]

        points = 10
        comment = f"Le pouvoir de {role} résonne !"
        lower_text = text.lower()
        
        if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'ensemble', 'toujours', 'tiako']):
            points = 20
            comment = "Puissance amoureuse maximale ! 💖"
        elif any(w in lower_text for w in ['sort', 'feu', 'temps', 'royaume', 'magie', 'pouvoir']):
            points = 15
            comment = f"Maîtrise parfaite du pouvoir '{power}' ! ⚡"

        if sender not in game_state["scores"]:
            game_state["scores"][sender] = 100
        game_state["scores"][sender] += points
        
        game_state["messages"].append({
            "sender": sender,
            "role": role,
            "avatar": avatar,
            "power": power,
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