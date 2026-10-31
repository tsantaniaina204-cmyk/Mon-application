from flask import Flask, render_template_string, request, jsonify

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
    <title>Le Remontage dans le Temps 💖</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body {
            height: 100%; width: 100%; overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
            display: flex; justify-content: center; align-items: center;
        }
        .chat-container {
            width: 100%; max-width: 450px; height: 100vh;
            background: #ffffff; display: flex; flex-direction: column;
            position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        @media (min-height: 600px) and (min-width: 460px) {
            .chat-container { height: 92vh; border-radius: 20px; overflow: hidden; }
        }
        .chat-header {
            background: #0f4c81; color: white; padding: 12px;
            text-align: center; font-weight: bold; font-size: 1.1em;
            display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;
        }
        .header-btn {
            background: rgba(255,255,255,0.2); color: white; border: none;
            padding: 4px 8px; border-radius: 12px; font-size: 0.75em; cursor: pointer;
        }
        .scores-board {
            display: flex; justify-content: space-around; background: #e8f4f8;
            padding: 8px; font-weight: bold; color: #1f4068; font-size: 0.8em;
            border-bottom: 1px solid #d1e8e2; flex-shrink: 0; overflow-x: auto;
        }
        .config-bar {
            padding: 8px; background: #f4f4f4; border-bottom: 1px solid #ddd;
            display: flex; flex-direction: column; gap: 6px; flex-shrink: 0;
        }
        .config-row { display: flex; gap: 6px; }
        select, input {
            flex: 1; padding: 6px; border-radius: 6px;
            border: 1px solid #ccc; font-size: 0.8em; background: #fff;
        }
        .chat-messages {
            flex: 1; padding: 12px; overflow-y: auto; background: #f7f9fb;
            display: flex; flex-direction: column; gap: 10px;
        }
        .msg-wrapper { display: flex; align-items: flex-start; gap: 8px; }
        .avatar-box {
            width: 40px; height: 40px; border-radius: 50%;
            background: #e4e4e4; display: flex; align-items: center; justify-content: center;
            font-size: 1.4em; box-shadow: 0 2px 5px rgba(0,0,0,0.15); flex-shrink: 0;
            border: 2px solid #0f4c81;
        }
        .msg-bubble {
            max-width: 70%; padding: 10px 12px; border-radius: 12px;
            font-size: 0.85em; position: relative; background: #ffffff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #e1e1e1;
        }
        .msg-header-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; }
        .msg-sender { font-weight: bold; color: #0f4c81; font-size: 0.85em; }
        .delete-btn {
            background: none; border: none; color: #ff6b6b; cursor: pointer;
            font-size: 0.9em; padding: 0 4px;
        }
        .power-tag {
            font-size: 0.7em; background: #fff3cd; color: #856404;
            padding: 2px 6px; border-radius: 4px; margin-bottom: 4px; display: inline-block;
            font-weight: bold;
        }
        .judge-note {
            font-size: 0.75em; margin-top: 5px; font-style: italic; color: #555;
            border-top: 1px dashed #eee; padding-top: 3px;
        }
        .chat-input-area {
            padding: 8px; background: #fff; border-top: 1px solid #ddd;
            display: flex; gap: 6px; flex-shrink: 0; align-items: center;
        }
        .send-btn {
            background: #0f4c81; color: white; border: none; padding: 0 16px;
            height: 38px; border-radius: 20px; font-weight: bold; cursor: pointer;
        }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        <span>⏳ Chrono-Royaume Magique 🔮</span>
        <button class="header-btn" onclick="resetGame()">🔄 Reset</button>
    </div>

    <div class="scores-board" id="scores-board">
        <span>Aucun score pour l'instant</span>
    </div>

    <div class="config-bar">
        <div class="config-row">
            <input type="text" id="username" placeholder="Ton Prénom (ex: Tiffanie, Tsanta...)" value="Tsanta">
            <select id="role">
                <option value="Sorcier">🔮 Sorcier (Pouvoir d'Ombre)</option>
                <option value="Magicien">✨ Magicien (Pouvoir Stellaire)</option>
                <option value="Guerrier">🗡️ Guerrier (Pouvoir de Feu)</option>
                <option value="Mage">📜 Mage (Pouvoir Ancien)</option>
                <option value="Roi/Reine">👑 Roi/Reine (Pouvoir Royal)</option>
                <option value="Voyageur">⏳ Voyageur (Pouvoir Temporel)</option>
            </select>
        </div>
        <div class="config-row">
            <select id="scenario">
                <option value="Le Royaume Effondré">🏰 Scénario : Le Royaume Effondré (Riches vs Pauvres)</option>
                <option value="La Faille Temporelle">⚡ Scénario : Réécrire une erreur du passé</option>
                <option value="Le Labyrinthe des Âmes">🌀 Scénario : Trouver la sortie ensemble</option>
                <option value="L'Ère des Dragons">🐉 Scénario : Affronter le gardien du temps</option>
            </select>
        </div>
    </div>

    <div class="chat-messages" id="chat-box"></div>

    <div class="chat-input-area">
        <input type="text" id="msg-input" placeholder="Invoque ta réplique ou discute..." onkeypress="checkEnter(event)">
        <button class="send-btn" onclick="sendMessage()">Lancer</button>
    </div>
</div>

<script>
async function sendMessage() {
    const username = document.getElementById('username').value.trim() || 'Anonyme';
    const role = document.getElementById('role').value;
    const scenario = document.getElementById('scenario').value;
    const text = document.getElementById('msg-input').value;

    if (!text.trim()) return;
    document.getElementById('msg-input').value = '';

    await fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ sender: username, role, scenario, text })
    });

    updateChat();
}

function checkEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

async function deleteMsg(index) {
    await fetch('/api/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ index })
    });
    updateChat();
}

async function resetGame() {
    if (confirm("Voulez-vous réinitialiser toute la partie ?")) {
        await fetch('/api/reset', { method: 'POST' });
        updateChat();
    }
}

async function updateChat() {
    const res = await fetch('/api/get');
    const data = await res.json();
    
    const box = document.getElementById('chat-box');
    box.innerHTML = '';

    data.messages.forEach((m, index) => {
        box.innerHTML += `
            <div class="msg-wrapper">
                <div class="avatar-box">${m.avatar}</div>
                <div class="msg-bubble">
                    <div class="msg-header-info">
                        <span class="msg-sender">${m.sender} (${m.role})</span>
                        <button class="delete-btn" onclick="deleteMsg(${index})" title="Supprimer">❌</button>
                    </div>
                    <div class="power-tag">⚡ ${m.power}</div>
                    <div>${m.text}</div>
                    <div class="judge-note">⚖️ ${m.comment} (+${m.points} pts)</div>
                </div>
            </div>
        `;
    });
    box.scrollTop = box.scrollHeight;

    const scoresBoard = document.getElementById('scores-board');
    scoresBoard.innerHTML = '';
    const scores = data.scores;
    if (Object.keys(scores).length === 0) {
        scoresBoard.innerHTML = '<span>Aucun score pour l\'instant</span>';
    } else {
        for (let [user, pts] of Object.entries(scores)) {
            scoresBoard.innerHTML += `<span>${user}: ${pts} pts</span>`;
        }
    }
}

setInterval(updateChat, 2000);
window.onload = updateChat;
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/send', methods=['POST'])
def send():
    data = request.json
    sender = data.get('sender', 'Anonyme')
    role = data.get('role', 'Sorcier')
    scenario = data.get('scenario', 'Général')
    text = data.get('text', '')
    
    # Attribution automatique des avatars et des pouvoirs spéciaux selon le rôle choisi
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

    # Juge automatique intégré
    points = 10
    comment = f"Le pouvoir de {role} résonne dans le temps !"
    lower_text = text.lower()
    
    if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'ensemble', 'toujours', 'tiako']):
        points = 20
        comment = "Puissance amoureuse maximale ! Le juge est conquis. 💖"
    elif any(w in lower_text for w in ['sort', 'feu', 'temps', 'royaume', 'magie', 'pouvoir']):
        points = 15
        comment = f"Utilisation magistrale du pouvoir '{power}' ! ⚡"

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
    
    return jsonify({"status": "ok"})

@app.route('/api/delete', methods=['POST'])
def delete_msg():
    data = request.json
    index = data.get('index')
    if index is not None and 0 <= index < len(game_state["messages"]):
        game_state["messages"].pop(index)
    return jsonify({"status": "ok"})

@app.route('/api/get')
def get_data():
    return jsonify(game_state)

@app.route('/api/reset', methods=['POST'])
def reset_data():
    game_state["messages"] = []
    game_state["scores"] = {}
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)