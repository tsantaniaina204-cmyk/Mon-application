from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {"Tsanta": 100, "Tiffanie": 100}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Le Remontage dans le Temps 💖</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
            margin: 0;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .chat-container {
            width: 100%;
            max-width: 450px;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            height: 90vh;
        }
        .chat-header {
            background: #e91e63;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .scores-board {
            display: flex;
            justify-content: space-around;
            background: #fff0f5;
            padding: 8px;
            font-weight: bold;
            color: #c2185b;
            font-size: 0.85em;
            border-bottom: 1px solid #ffd1dc;
        }
        .config-bar {
            padding: 10px;
            background: #fafafa;
            border-bottom: 1px solid #eee;
            display: flex;
            gap: 8px;
        }
        select {
            flex: 1;
            padding: 6px;
            border-radius: 6px;
            border: 1px solid #ffb6c1;
            font-size: 0.8em;
        }
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #fdfdfd;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg-wrapper {
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }
        .msg-wrapper.tsanta {
            flex-direction: row-reverse;
        }
        .avatar-img {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: #ffb6c1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }
        .msg-bubble {
            max-width: 70%;
            padding: 10px 14px;
            border-radius: 15px;
            font-size: 0.9em;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .tsanta .msg-bubble {
            background: #e91e63;
            color: white;
            border-bottom-right-radius: 2px;
        }
        .tiffanie .msg-bubble {
            background: #f1f0f0;
            color: #333;
            border-bottom-left-radius: 2px;
        }
        .judge-note {
            font-size: 0.75em;
            margin-top: 4px;
            font-style: italic;
            opacity: 0.85;
            border-top: 1px dashed rgba(0,0,0,0.1);
            padding-top: 2px;
        }
        .chat-input-area {
            padding: 10px;
            background: #fff;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
        }
        input {
            flex: 1;
            padding: 10px;
            border-radius: 20px;
            border: 1px solid #ddd;
            outline: none;
            font-size: 0.9em;
        }
        button {
            background: #e91e63;
            color: white;
            border: none;
            padding: 0 16px;
            border-radius: 20px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background: #d81b60; }
    </style>
</head>
<body>

<div class="chat-container">
    <div class="chat-header">
        ⏳ Le Remontage dans le Temps 💖
    </div>

    <div class="scores-board">
        <span id="score-tsanta">Tsanta: 100 pts</span>
        <span id="score-tiff">Tiffanie: 100 pts</span>
    </div>

    <div class="config-bar">
        <select id="username">
            <option value="Tsanta">Moi : Tsanta</option>
            <option value="Tiffanie">Moi : Tiffanie</option>
        </select>
        <select id="scenario">
            <option value="Inversion de Richesse">🎭 Riche vs Pauvre</option>
            <option value="Dispute du Passé">⏳ Malentendu du Passé</option>
            <option value="Première Rencontre">✨ Premier Regard</option>
        </select>
    </div>

    <div class="chat-messages" id="chat-box"></div>

    <div class="chat-input-area">
        <input type="text" id="msg-input" placeholder="Écris ton message d'amour..." onkeypress="checkEnter(event)">
        <button onclick="sendMessage()">Envoyer</button>
    </div>
</div>

<script>
async function sendMessage() {
    const username = document.getElementById('username').value;
    const scenario = document.getElementById('scenario').value;
    const text = document.getElementById('msg-input').value;

    if (!text.trim()) return;
    document.getElementById('msg-input').value = '';

    await fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ sender: username, scenario, text })
    });

    updateChat();
}

function checkEnter(e) {
    if (e.key === 'Enter') sendMessage();
}

async function updateChat() {
    const res = await fetch('/api/get');
    const data = await res.json();
    
    const box = document.getElementById('chat-box');
    box.innerHTML = '';

    data.messages.forEach(m => {
        const isTsanta = m.sender === 'Tsanta';
        const cssClass = isTsanta ? 'tsanta' : 'tiffanie';
        // Avatars codés sur mesure
        const avatarIcon = isTsanta ? '👨‍💻' : '🌸';

        box.innerHTML += `
            <div class="msg-wrapper ${cssClass}">
                <div class="avatar-img">${avatarIcon}</div>
                <div class="msg-bubble">
                    <div style="font-weight: bold; font-size: 0.8em; margin-bottom: 2px;">${m.sender}</div>
                    <div>${m.text}</div>
                    <div class="judge-note">⚖️ ${m.comment} (${m.points > 0 ? '+' + m.points : m.points} pts)</div>
                </div>
            </div>
        `;
    });
    box.scrollTop = box.scrollHeight;

    document.getElementById('score-tsanta').innerText = `Tsanta: ${data.scores.Tsanta} pts`;
    document.getElementById('score-tiff').innerText = `Tiffanie: ${data.scores.Tiffanie} pts`;
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
    sender = data.get('sender', 'Tsanta')
    text = data.get('text', '')
    
    lower_text = text.lower()
    points = 5
    comment = "Le juge valide cette réplique !"
    
    if any(w in lower_text for w in ['amour', 't’aime', 'je t aime', 'coeur', 'vie', 'toujours', 'ensemble', 'tiako', 'mandrasa']):
        points = 15
        comment = "Coup de cœur romantique absolu ! 💕"
    elif any(w in lower_text for w in ['riche', 'pauvre', 'argent', 'passé', 'temps', 'regard']):
        points = 10
        comment = "Excellente immersion dans le jeu ! 🎭"
    elif len(text) < 5:
        points = 2
        comment = "Un peu court, dis-en plus ! 😉"

    game_state["scores"][sender] += points
    
    game_state["messages"].append({
        "sender": sender,
        "text": text,
        "comment": comment,
        "points": points
    })
    
    return jsonify({"status": "ok"})

@app.route('/api/get')
def get_data():
    return jsonify(game_state)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)