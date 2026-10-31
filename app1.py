from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Base de données en mémoire pour le jeu
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
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%);
            margin: 0;
            padding: 15px;
            color: #4a4a4a;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: auto;
        }
        h1 { text-align: center; color: #e91e63; font-size: 1.5em; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #c2185b; font-size: 0.85em; margin-bottom: 15px; }
        .config-box { margin-bottom: 15px; background: #fff0f5; padding: 12px; border-radius: 12px; }
        select, input, button {
            width: 100%;
            padding: 10px;
            margin-top: 6px;
            border-radius: 8px;
            border: 1px solid #ffb6c1;
            box-sizing: border-box;
        }
        button {
            background-color: #e91e63;
            color: white;
            font-weight: bold;
            border: none;
            cursor: pointer;
            margin-top: 10px;
        }
        #chat-box {
            height: 220px;
            overflow-y: auto;
            border: 1px solid #ffd1dc;
            padding: 10px;
            border-radius: 10px;
            background: #fff;
            margin-bottom: 10px;
        }
        .msg { margin-bottom: 10px; font-size: 0.9em; border-bottom: 1px dashed #eee; padding-bottom: 5px; }
        .msg-sender { font-weight: bold; color: #d81b60; }
        .judge-comment {
            color: #880e4f;
            font-style: italic;
            font-size: 0.8em;
            background: #ffe4e1;
            padding: 4px 8px;
            border-radius: 6px;
            margin-top: 4px;
        }
        .scores-board {
            display: flex;
            justify-content: space-around;
            background: #ffe4e1;
            padding: 8px;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #c2185b;
            font-size: 0.9em;
        }
    </style>
</head>
<body>

<div class="card">
    <h1>⏳ Le Remontage dans le Temps 💖</h1>
    <div class="subtitle">Pour Tsanta & Tiffanie</div>

    <div class="scores-board">
        <span id="score-tsanta">Tsanta: 100 pts</span>
        <span id="score-tiff">Tiffanie: 100 pts</span>
    </div>

    <div class="config-box">
        <label><b>Qui es-tu ?</b></label>
        <select id="username">
            <option value="Tsanta">Tsanta</option>
            <option value="Tiffanie">Tiffanie</option>
        </select>

        <label style="margin-top: 8px; display: block;"><b>Situation / Scénario :</b></label>
        <select id="scenario">
            <option value="Riche vs Pauvre">Inversion : L'un est millionnaire, l'autre bohème</option>
            <option value="Dispute du Passé">Résolution d'un malentendu temporel</option>
            <option value="Première Rencontre">Revivre le premier regard</option>
        </select>
    </div>

    <div id="chat-box"></div>

    <input type="text" id="msg-input" placeholder="Écris ta réplique pleine d'amour...">
    <button onclick="sendMessage()">Envoyer 💕</button>
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

async function updateChat() {
    const res = await fetch('/api/get');
    const data = await res.json();
    
    const box = document.getElementById('chat-box');
    box.innerHTML = '';

    data.messages.forEach(m => {
        box.innerHTML += `
            <div class="msg">
                <span class="msg-sender">${m.sender} :</span> ${m.text}
                <div class="judge-comment">⚖️ Juge : "${m.comment}" (${m.points > 0 ? '+' + m.points : m.points} pts)</div>
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
    sender = data.get('sender', 'Anonyme')
    text = data.get('text', '')
    
    # Juge automatique intégré en Python (analyse des mots-clés)
    lower_text = text.lower()
    points = 5
    comment = "C'est mignon tout plein !"
    
    if any(w in lower_text for w in ['amour', 't’aime', 'je t aime', 'coeur', 'vie', 'toujours', 'ensemble', 'tiako']):
        points = 12
        comment = "Quel romantisme absolu ! Le cœur du juge fond. 💖"
    elif any(w in lower_text for w in ['pauvre', 'riche', 'argent', 'million', 'sou', 'passé', 'temps']):
        points = 8
        comment = "Excellente mise en situation dans le scénario ! 🎭"
    elif len(text) < 8:
        points = 2
        comment = "Un peu court ! Dis-en un peu plus avec ton cœur. 😉"

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