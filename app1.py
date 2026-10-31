from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {},
    "winner": None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Pouvoirs & Victoire</title>
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
        
        /* Styles spéciaux pour les attaques et descriptions de pouvoirs */
        .msg-bubble.attack-frog {
            background: linear-gradient(135deg, #1e4620, #0f2611);
            border: 2px solid #4caf50;
        }
        .msg-bubble.attack-dragon {
            background: linear-gradient(135deg, #4a1515, #260a0a);
            border: 2px solid #ff5722;
        }
        .msg-bubble.attack-snake {
            background: linear-gradient(135deg, #3d1b4e, #1e0d26);
            border: 2px solid #9c27b0;
        }
        .msg-bubble.power-info {
            background: linear-gradient(135deg, #1f3a5f, #112238);
            border: 2px solid #0084ff;
            color: #e4e6eb;
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
        }

        /* ÉCRAN DE VICTOIRE */
        .victory-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
            text-align: center;
            padding: 20px;
        }
        .victory-card {
            background: linear-gradient(135deg, #0f4c81, #162447);
            border: 3px solid #ffD700;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .victory-title {
            font-size: 2em;
            color: #ffD700;
            margin-bottom: 10px;
        }
        .victory-name {
            font-size: 1.5em;
            color: #ffffff;
            margin-bottom: 20px;
            font-weight: bold;
        }
        .victory-btn {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💬 Chrono-Royaume & Pouvoirs</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    {% if winner %}
    <div class="victory-overlay">
        <div class="victory-card">
            <div class="victory-title">🎉 VICTOIRE ÉPIQUE ! 👑</div>
            <div class="victory-name">Félicitations au grand vainqueur :<br><span style="color: #00ffff;">{{ winner }}</span></div>
            <p style="color: #e4e6eb; margin-bottom: 20px; font-size: 0.9em;">L'adversaire est tombé à 0 point !</p>
            <a href="/reset" class="victory-btn">Nouvelle Partie 🔄</a>
        </div>
    </div>
    {% endif %}

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <input type="text" name="username" placeholder="Votre Nom (ex: Tsanta, Tiffanie...)" autocomplete="off">
                <input type="text" name="role" placeholder="Rôle (ex: Sorcier)" value="Sorcier" required>
            </div>
            <div class="config-row">
                <input type="text" name="scenario" placeholder="Scénario (ex: Drague, Aventure...)" value="Drague Magique" required>
            </div>
            
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

        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble {{ m.extra_class }}">
                            {% if not m.is_system %}
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            {% endif %}
                            {{ m.text }}
                            {% if not m.is_system %}
                            <div class="judge-info">🌐 [{{ m.scenario }}] ⚖️ {{ m.comment }} (+{{ m.points }}pts)</div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

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
    return render_template_string(HTML_TEMPLATE, messages=game_state["messages"], scores=game_state["scores"], winner=game_state["winner"])

@app.route('/send', methods=['POST'])
def send():
    if game_state["winner"]:
        return redirect(url_for('index'))

    sender = request.form.get('username', '').strip() or 'Anonyme'
    role = request.form.get('role', 'Personnage').strip() or 'Personnage'
    scenario = request.form.get('scenario', 'Libre').strip() or 'Libre'
    text = request.form.get('text', '').strip()
    
    if text:
        avatar = "💬"
        extra_class = ""
        points = 10
        comment = f"Réplique validée dans '{scenario}' !"

        lower_text = text.lower()
        
        # Vérifier si c'est un message d'attaque d'animal
        if lower_text.startswith('/grenouille'):
            content = text.replace('/grenouille', '').strip() or 'le vide'
            avatar = "🐸"
            extra_class = "attack-frog"
            text = f"🐸 **ATTAQUE GÉANTE !** Une immense grenouille verte surgit et **gobe d'un coup de langue** : *« {content} »* 👅✨"
            points = 25
            comment = "Attaque amphibie spectaculaire !"
        elif lower_text.startswith('/dragon'):
            content = text.replace('/dragon', '').strip() or 'le vide'
            avatar = "🐉"
            extra_class = "attack-dragon"
            text = f"🐉 **FEU DU DRAGON !** Un dragon colossal calcine et dévore : *« {content} »* 🔥💥"
            points = 30
            comment = "Carnage draconien absolu !"
        elif lower_text.startswith('/serpent'):
            content = text.replace('/serpent', '').strip() or 'le vide'
            avatar = "🐍"
            extra_class = "attack-snake"
            text = f"🐍 **CONSTRICTION MYSTIQUE !** Un serpent légendaire avale tout rond : *« {content} »* 🌀🌿"
            points = 25
            comment = "Attaque serpentine foudroyante !"
        else:
            emojis = {"sorcier": "🧙‍♂️", "magicien": "✨", "guerrier": "🗡️", "roi": "👑", "reine": "👑", "voyageur": "⏳"}
            role_key = role.lower()
            avatar = emojis.get(role_key, "🔮")
            
            if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'tiako', 'mandrasa']):
                points = 20
                comment = "Coup de cœur romantique absolu !"

            # Créer un message d'explication du pouvoir si c'est la première fois ou selon le rôle
            powers_db = {
                "sorcier": {
                    "action": "invoquer des arcanes ténébreux et altérer la perception du temps",
                    "pouvoir": "Magie Noire & Illusions",
                    "usage": "Créer des fausses réalités et manipuler l'esprit de l'adversaire"
                },
                "magicien": {
                    "action": "canalisant les énergies stellaires pour plier les lois physiques",
                    "pouvoir": "Sortilèges Stellaires",
                    "usage": "Foudroyer les obstacles et illuminer le dialogue de lumière pure"
                },
                "guerrier": {
                    "action": "se positionner en première ligne avec une force implacable",
                    "pouvoir": "Frappe de Feu Sacré",
                    "usage": "Briser les défenses ennemies par la puissance brute"
                }
            }
            
            p_info = powers_db.get(role_key, {
                "action": f"manier l'art unique du rôle de {role}",
                "pouvoir": f"Puissance de {role}",
                "usage": "Surprendre l'adversaire avec des aptitudes inattendues"
            })

            # Ajouter un message d'explication du pouvoir avant le message de l'utilisateur
            game_state["messages"].append({
                "sender": f"Système ({role})",
                "role": "Guide",
                "scenario": scenario,
                "avatar": "⚡",
                "text": f"🔮 **[Révélation du Pouvoir]** : Le personnage **{role}** entre en scène pour **{p_info['action']}**.\n• **Pouvoir :** {p_info['pouvoir']}\n• **Utilisation :** {p_info['usage']}",
                "comment": "Description du rôle",
                "points": 0,
                "extra_class": "power-info",
                "is_system": True
            })

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
            "extra_class": extra_class,
            "is_system": False
        })
        
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_msg(index):
    if game_state["winner"]:
        return redirect(url_for('index'))

    if 0 <= index < len(game_state["messages"]):
        msg = game_state["messages"].pop(index)
        if not msg.get("is_system", False):
            author = msg["sender"]
            penalty = msg["points"]
            
            if author in game_state["scores"]:
                game_state["scores"][author] -= penalty
                if game_state["scores"][author] < 0:
                    game_state["scores"][author] = 0

                for user, pts in game_state["scores"].items():
                    if pts <= 0:
                        other_users = [u for u in game_state["scores"].keys() if u != user]
                        game_state["winner"] = other_users[0] if other_users else "Le Joueur Survivant"

    return redirect(url_for('index'))

@app.route('/reset')
def reset_data():
    game_state["messages"] = []
    game_state["scores"] = {}
    game_state["winner"] = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)