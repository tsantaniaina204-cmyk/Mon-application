from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {"Séducteur": 50, "Défenseur (Cible)": 50},
    "winner": None,
    "last_animal": None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Duel Stratégique & Intelligence</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        html, body {
            height: 100%; width: 100%;
            background-color: #18191a; color: #e4e6eb;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
        }

        .messenger-container {
            display: flex; flex-direction: column;
            height: 100vh; height: 100dvh;
            max-width: 480px; margin: 0 auto;
            background-color: #242526; position: relative;
        }

        .messenger-header {
            flex-shrink: 0; background-color: #242526;
            padding: 10px 14px; display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid #393a3b; z-index: 10;
        }
        .header-title { font-weight: bold; font-size: 1em; color: #ff69b4; }
        .reset-btn {
            background: #3a3b3c; color: #b0b3b8; border: none;
            padding: 6px 12px; border-radius: 12px; font-size: 0.8em; text-decoration: none; cursor: pointer;
        }

        .messenger-form { display: flex; flex-direction: column; flex: 1; min-height: 0; }

        .top-panel {
            flex-shrink: 0; background-color: #242526;
            padding: 8px 12px; border-bottom: 1px solid #393a3b; font-size: 0.8em;
        }
        .config-row { display: flex; gap: 6px; margin-bottom: 6px; }
        input[type="text"], select {
            flex: 1; background-color: #3a3b3c; border: 1px solid #393a3b; color: #e4e6eb;
            padding: 8px 12px; border-radius: 16px; font-size: 0.85em; outline: none;
        }
        input[type="text"]:focus, select:focus { border-color: #ff69b4; }
        
        .scores-board {
            display: flex; justify-content: center; gap: 15px;
            background-color: #1c1d1e; padding: 6px; border-radius: 10px;
            color: #ff69b4; font-weight: bold; font-size: 0.85em; margin-top: 4px; overflow-x: auto;
        }

        .chat-messages {
            flex: 1; overflow-y: auto; padding: 12px;
            background-color: #18191a; display: flex; flex-direction: column; gap: 12px; min-height: 0;
        }
        .msg-row { display: flex; align-items: flex-end; gap: 8px; }
        .avatar-circle {
            width: 34px; height: 34px; border-radius: 50%; background-color: #3a3b3c;
            display: flex; align-items: center; justify-content: center; font-size: 1.1em; flex-shrink: 0; border: 1px solid #ff69b4;
        }
        .msg-content { max-width: 82%; display: flex; flex-direction: column; }
        .msg-bubble {
            background-color: #3a3b3c; color: #e4e6eb; padding: 10px 14px;
            border-radius: 18px; font-size: 0.9em; word-wrap: break-word; position: relative;
        }
        .msg-bubble.animal-strategy {
            background: linear-gradient(135deg, #4a1535, #260a1d);
            border: 2px solid #ff69b4;
        }
        .msg-sender { font-size: 0.75em; color: #b0b3b8; margin-bottom: 3px; margin-left: 4px; }
        .judge-info {
            font-size: 0.75em; color: #ffb6c1; margin-top: 4px; font-style: italic;
            border-top: 1px dashed rgba(255,255,255,0.15); padding-top: 3px;
        }
        .delete-link { color: #ff5252; font-size: 0.8em; text-decoration: none; float: right; margin-left: 8px; font-weight: bold; }

        .messenger-input-area {
            flex-shrink: 0; background-color: #242526; padding: 12px 14px;
            border-top: 1px solid #393a3b; display: flex; align-items: center; gap: 10px; min-height: 64px;
        }
        .message-input {
            flex: 1; background-color: #3a3b3c; border: 1px solid #4e4f50; color: #e4e6eb;
            padding: 12px 18px; border-radius: 24px; font-size: 0.95em; outline: none; height: 44px;
        }
        .message-input::placeholder { color: #b0b3b8; }
        .send-btn {
            background-color: #ff69b4; color: white; border: none; width: 44px; height: 44px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 1.2em; flex-shrink: 0;
        }

        .victory-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; text-align: center; padding: 20px;
        }
        .victory-card {
            background: linear-gradient(135deg, #4a1535, #162447); border: 3px solid #ff69b4;
            padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .victory-title { font-size: 2em; color: #ff69b4; margin-bottom: 10px; }
        .victory-name { font-size: 1.5em; color: #ffffff; margin-bottom: 20px; font-weight: bold; }
        .victory-btn {
            background-color: #ff69b4; color: white; border: none; padding: 12px 24px;
            border-radius: 25px; font-size: 1.1em; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block;
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💖 Duel Stratégique & Intelligence</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    {% if winner %}
    <div class="victory-overlay">
        <div class="victory-card">
            <div class="victory-title">🎉 VICTOIRE ÉPIQUE DE L'AMOUR ! 💘</div>
            <div class="victory-name">Le grand vainqueur par ruse et séduction :<br><span style="color: #00ffff;">{{ winner }}</span></div>
            <p style="color: #e4e6eb; margin-bottom: 20px; font-size: 0.9em;">L'adversaire a succombé face à tant d'intelligence !</p>
            <a href="/reset" class="victory-btn">Nouvelle Partie 🔄</a>
        </div>
    </div>
    {% endif %}

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <input type="text" name="username" placeholder="Votre Nom (ex: Tsanta, Tiffanie)" autocomplete="off">
                <select name="role">
                    <option value="Séducteur Charmant">🤵 Séducteur Charmant</option>
                    <option value="Poète Romantique">📜 Poète Romantique</option>
                    <option value="Mystique ténébreux">🖤 Mystique Ténébreux</option>
                    <option value="Princesse / Reine">👸 Princesse / Reine</option>
                    <option value="Aventurier Passionné">🧭 Aventurier Passionné</option>
                </select>
            </div>
            
            <div class="scores-board">
                <span>🌡️ JAUGE D'AMOUR :</span>
                {% for user, pts in scores.items() %}
                    <span>{{ user }} : {{ pts }}%</span>
                {% endfor %}
            </div>
        </div>

        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble {{ m.extra_class }}">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            {{ m.text }}
                            <div class="judge-info">💡 {{ m.comment }}</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa Message (ex: /lapin Si le lion est fort, face à l'éléphant...)" required autocomplete="off">
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
    return render_template_string(HTML_TEMPLATE, messages=game_state["messages"], scores=game_state["scores"], winner=game_state["winner"])

@app.route('/send', methods=['POST'])
def send():
    if game_state["winner"]:
        return redirect(url_for('index'))

    sender = request.form.get('username', '').strip() or 'Anonyme'
    role = request.form.get('role', 'Séducteur Charmant')
    text = request.form.get('text', '').strip()
    
    if text:
        lower_text = text.lower()
        avatar = "👤"
        extra_class = ""
        impact = 10
        comment = "Message de drague classique."

        animals_rules = {
            "/lion": {"name": "Lion", "emoji": "🦁", "beats": ["/loup", "/chat", "/lapin"]},
            "/loup": {"name": "Loup", "emoji": "🐺", "beats": ["/chat", "/lapin"]},
            "/chat": {"name": "Chat", "emoji": "🐱", "beats": ["/lapin"]},
            "/dragon": {"name": "Dragon", "emoji": "🐉", "beats": ["/lion", "/loup", "/chat", "/lapin"]},
            "/lapin": {"name": "Lapin", "emoji": "🐰", "beats": []}
        }

        matched_animal = None
        for cmd in animals_rules.keys():
            if lower_text.startswith(cmd):
                matched_animal = cmd
                break

        if matched_animal:
            curr_animal = animals_rules[matched_animal]
            avatar = curr_animal["emoji"]
            extra_class = "animal-strategy"

            # Détection d'intelligence (si le message contient une question piège ou de la logique philosophique/rhétorique)
            smart_keywords = ['si', 'pourquoi', 'comment', 'face à', 'contre', 'rien', 'force', 'esprit', 'malin', 'intelligence', 'stratégie']
            is_smart = any(k in lower_text for k in smart_keywords) and len(text.split()) > 5

            prev_animal = game_state.get("last_animal")

            if is_smart:
                # L'intelligence annule l'écart de force brut ! Le petit animal l'emporte par la ruse.
                impact = 40
                comment = f"🧠 Coup de génie ! Le {curr_animal['name']} utilise la ruse et une question piège imparable. L'écart de force est annulé, la cible succombe !"
            elif prev_animal and prev_animal != matched_animal:
                if matched_animal in animals_rules[prev_animal]["beats"]:
                    impact = 35
                    comment = f"⚔️ Victoire tactique ! Le {curr_animal['name']} domine l'animal adverse !"
                elif prev_animal in curr_animal["beats"]:
                    impact = -15
                    comment = f"🛡️ Contre-attaque subie ! L'adversaire était plus fort."
                else:
                    impact = 15
                    comment = f"⚖️ Égalité entre bêtes."
            else:
                if matched_animal == "/dragon":
                    impact = 50
                    comment = f"🔥 Puissance absolue du Dragon !"
                else:
                    impact = 20
                    comment = f"✨ Attaque du {curr_animal['name']} lancée !"

            game_state["last_animal"] = matched_animal

            # 1. Message d'alerte et de risque
            game_state["messages"].append({
                "sender": f"Système d'Alerte",
                "role": "Arbitre",
                "avatar": "⚠️",
                "text": f"⚠️ *[Analyse Taktike]* : Attaque du **{curr_animal['name']}**. {'🧠 Ruse détectée : Le piège logique annule les forces brutes !' if is_smart else 'Attention au rapport de force !'}",
                "comment": "Risque et décision tactique",
                "extra_class": "animal-strategy"
            })

            # 2. Message de l'attaque
            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": avatar,
                "text": text,
                "comment": comment,
                "extra_class": extra_class
            })

        else:
            game_state["last_animal"] = None
            if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'oui', 'tiako', 'ensemble', 'viens']):
                impact = 15
                comment = "💘 Déclaration romantique classique."
            else:
                impact = -5
                comment = "🛡️ Résistance active."

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "👤",
                "text": text,
                "comment": comment,
                "extra_class": ""
            })

        # Mise à jour de la jauge d'amour
        for p in game_state["scores"]:
            if p != sender:
                game_state["scores"][p] += impact
                if game_state["scores"][p] > 100:
                    game_state["scores"][p] = 100
                if game_state["scores"][p] <= 0:
                    game_state["scores"][p] = 0
                    game_state["winner"] = sender

    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_msg(index):
    if game_state["winner"]:
        return redirect(url_for('index'))
    if 0 <= index < len(game_state["messages"]):
        game_state["messages"].pop(index)
    return redirect(url_for('index'))

@app.route('/reset')
def reset_data():
    game_state["messages"] = []
    game_state["scores"] = {"Séducteur": 50, "Défenseur (Cible)": 50}
    game_state["winner"] = None
    game_state["last_animal"] = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)