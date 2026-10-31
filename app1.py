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
    <title>Chrono-Royaume - Attaques Animales</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        html, body {
            height: 100%;
            width: 100%;
            background-color: #18191a;
            color: #e4e6eb;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
        }

        .messenger-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            height: 100dvh;
            max-width: 480px;
            margin: 0 auto;
            background-color: #242526;
            position: relative;
        }

        .messenger-header {
            flex-shrink: 0;
            background-color: #242526;
            padding: 10px 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #393a3b;
            z-index: 10;
        }
        .header-title {
            font-weight: bold;
            font-size: 1em;
            color: #e4e6eb;
        }
        .reset-btn {
            background: #3a3b3c;
            color: #b0b3b8;
            border: none;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            text-decoration: none;
            cursor: pointer;
        }

        .messenger-form {
            display: flex;
            flex-direction: column;
            flex: 1;
            min-height: 0;
        }

        .top-panel {
            flex-shrink: 0;
            background-color: #242526;
            padding: 8px 12px;
            border-bottom: 1px solid #393a3b;
            font-size: 0.8em;
        }
        .config-row {
            display: flex;
            gap: 6px;
            margin-bottom: 6px;
        }
        input[type="text"] {
            flex: 1;
            background-color: #3a3b3c;
            border: 1px solid #393a3b;
            color: #e4e6eb;
            padding: 8px 12px;
            border-radius: 16px;
            font-size: 0.85em;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #0084ff;
        }
        
        /* Tableau des scores global et clair */
        .scores-board {
            display: flex;
            justify-content: center;
            gap: 15px;
            background-color: #1c1d1e;
            padding: 6px;
            border-radius: 10px;
            color: #0084ff;
            font-weight: bold;
            font-size: 0.85em;
            margin-top: 4px;
            overflow-x: auto;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background-color: #18191a;
            display: flex;
            flex-direction: column;
            gap: 12px;
            min-height: 0;
        }
        .msg-row {
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }
        .avatar-circle {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background-color: #3a3b3c;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1em;
            flex-shrink: 0;
            border: 1px solid #4e4f50;
        }
        .msg-content {
            max-width: 78%;
            display: flex;
            flex-direction: column;
        }
        .msg-bubble {
            background-color: #3a3b3c;
            color: #e4e6eb;
            padding: 10px 14px;
            border-radius: 18px;
            font-size: 0.9em;
            word-wrap: break-word;
            position: relative;
        }
        
        /* Style spécial pour les attaques d'animaux */
        .msg-bubble.attack-frog {
            background: linear-gradient(135deg, #1e4620, #0f2611);
            border: 2px solid #4caf50;
            animation: pulseAttack 0.5s ease;
        }
        .msg-bubble.attack-dragon {
            background: linear-gradient(135deg, #4a1515, #260a0a);
            border: 2px solid #ff5722;
        }
        .msg-bubble.attack-snake {
            background: linear-gradient(135deg, #3d1b4e, #1e0d26);
            border: 2px solid #9c27b0;
        }

        @keyframes pulseAttack {
            0% { transform: scale(0.95); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }

        .msg-sender {
            font-size: 0.75em;
            color: #b0b3b8;
            margin-bottom: 3px;
            margin-left: 4px;
        }
        .judge-info {
            font-size: 0.75em;
            color: #9cb4cc;
            margin-top: 4px;
            font-style: italic;
            border-top: 1px dashed rgba(255,255,255,0.15);
            padding-top: 3px;
        }
        .delete-link {
            color: #ff5252;
            font-size: 0.8em;
            text-decoration: none;
            float: right;
            margin-left: 8px;
            font-weight: bold;
        }

        .messenger-input-area {
            flex-shrink: 0;
            background-color: #242526;
            padding: 12px 14px;
            border-top: 1px solid #393a3b;
            display: flex;
            align-items: center;
            gap: 10px;
            min-height: 64px;
        }
        .message-input {
            flex: 1;
            background-color: #3a3b3c;
            border: 1px solid #4e4f50;
            color: #e4e6eb;
            padding: 12px 18px;
            border-radius: 24px;
            font-size: 1em;
            outline: none;
            height: 44px;
        }
        .message-input::placeholder {
            color: #b0b3b8;
        }
        .send-btn {
            background-color: #0084ff;
            color: white;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.2em;
            flex-shrink: 0;
            transition: background 0.2s, transform 0.1s;
        }
        .send-btn:active {
            transform: scale(0.92);
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💬 Chrono-Royaume & Bestiaire</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <!-- Champ nom sans valeur par défaut fixe -->
                <input type="text" name="username" placeholder="Votre Nom (ex: Tsanta, Tiffanie...)" autocomplete="off">
                <input type="text" name="role" placeholder="Rôle (ex: Sorcier)" value="Sorcier" required>
            </div>
            <div class="config-row">
                <input type="text" name="scenario" placeholder="Scénario (ex: Drague, Aventure...)" value="Drague Magique" required>
            </div>
            
            <!-- Tableau des scores général affichant tous les participants -->
            <div class="scores-board">
                <span>🏆 SCORES :</span>
                {% if scores %}
                    {% for user, pts in scores.items() %}
                        <span>{{ user }} : {{ pts }} pts</span>
                    {% endfor %}
                {% else %}
                    <span>Aucun point pour l'instant</span>
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
                        <div class="msg-bubble {{ m.extra_class }}">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            {{ m.text }}
                            <div class="judge-info">🌐 [{{ m.scenario }}] ⚖️ {{ m.comment }} (+{{ m.points }}pts)</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <!-- Barre de saisie -->
        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa Message (ex: /grenouille Bonjour)..." required autocomplete="off">
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
    sender = request.form.get('username', '').strip() or 'Anonyme'
    role = request.form.get('role', 'Personnage').strip() or 'Personnage'
    scenario = request.form.get('scenario', 'Libre').strip() or 'Libre'
    text = request.form.get('text', '').strip()
    
    if text:
        avatar = "💬"
        extra_class = ""
        points = 10
        comment = f"Réplique validée dans '{scenario}' !"

        # Gestion des attaques d'animaux spectaculaires (/grenouille, /dragon, /serpent)
        lower_text = text.lower()
        if lower_text.startswith('/grenouille'):
            content = text.replace('/grenouille', '').strip() or 'le vide'
            avatar = "🐸"
            extra_class = "attack-frog"
            text = f"🐸 **ATTAQUE GÉANTE !** Une immense grenouille verte surgit des marécages et **gobe d'un coup de langue fulgurant** le message : *« {content} »* 👅✨"
            points = 25
            comment = "Attaque amphibie spectaculaire !"
        elif lower_text.startswith('/dragon'):
            content = text.replace('/dragon', '').strip() or 'le vide'
            avatar = "🐉"
            extra_class = "attack-dragon"
            text = f"🐉 **FEU DU DRAGON !** Un dragon colossal descend du ciel et **calcine et dévore** le message : *« {content} »* 🔥💥"
            points = 30
            comment = "Carnage draconien absolu !"
        elif lower_text.startswith('/serpent'):
            content = text.replace('/serpent', '').strip() or 'le vide'
            avatar = "🐍"
            extra_class = "attack-snake"
            text = f"🐍 **CONSTRICTION MYSTIQUE !** Un serpent légendaire surgit de l'ombre et **s'enroule pour avaler tout rond** le message : *« {content} »* 🌀🌿"
            points = 25
            comment = "Attaque serpentine foudroyante !"
        else:
            # Attribution d'un avatar selon le rôle classique
            emojis = {"sorcier": "🧙‍♂️", "magicien": "✨", "guerrier": "🗡️", "roi": "👑", "reine": "👑", "voyageur": "⏳"}
            avatar = emojis.get(role.lower(), "💬")
            if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'tiako', 'mandrasa']):
                points = 20
                comment = "Coup de cœur romantique absolu !"

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
            "points": points,
            "extra_class": extra_class
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