from flask import Flask, render_template_string, request, redirect, url_for
import re

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {"Séducteur": 50, "Défenseur (Cible)": 50},
    "winner": None,
    "last_animal_power": 0,
    "last_animal_name": None,
    "shield_used": {}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Duel Stratégique & Économie de Points</title>
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
        .header-title { font-weight: bold; font-size: 1em; color: #00bfff; }
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
        input[type="text"]:focus, select:focus { border-color: #00bfff; }
        
        .scores-board {
            display: flex; justify-content: center; gap: 15px;
            background-color: #1c1d1e; padding: 6px; border-radius: 10px;
            color: #00bfff; font-weight: bold; font-size: 0.85em; margin-top: 4px; overflow-x: auto;
        }

        .chat-messages {
            flex: 1; overflow-y: auto; padding: 12px;
            background-color: #18191a; display: flex; flex-direction: column; gap: 12px; min-height: 0;
        }
        .msg-row { display: flex; align-items: flex-end; gap: 8px; }
        .avatar-circle {
            width: 34px; height: 34px; border-radius: 50%; background-color: #3a3b3c;
            display: flex; align-items: center; justify-content: center; font-size: 1.1em; flex-shrink: 0; border: 1px solid #00bfff;
        }
        .msg-content { max-width: 82%; display: flex; flex-direction: column; }
        .msg-bubble {
            background-color: #3a3b3c; color: #e4e6eb; padding: 10px 14px;
            border-radius: 18px; font-size: 0.9em; word-wrap: break-word; position: relative;
        }
        .msg-bubble.animal-strategy {
            background: linear-gradient(135deg, #003366, #112233);
            border: 2px solid #00bfff;
        }
        .msg-sender { font-size: 0.75em; color: #b0b3b8; margin-bottom: 3px; margin-left: 4px; }
        .judge-info {
            font-size: 0.8em; color: #ffffff; background: rgba(0, 191, 255, 0.25);
            margin-top: 6px; padding: 6px; border-radius: 8px; font-weight: bold;
            border-left: 3px solid #00bfff;
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
            background-color: #00bfff; color: white; border: none; width: 44px; height: 44px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 1.2em; flex-shrink: 0;
        }

        .victory-overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.92); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; text-align: center; padding: 20px;
        }
        .victory-card {
            background: linear-gradient(135deg, #003366, #162447); border: 3px solid #00bfff;
            padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .victory-title { font-size: 1.8em; color: #00bfff; margin-bottom: 10px; }
        .victory-flowers { font-size: 1.5em; margin: 10px 0; }
        .victory-name { font-size: 1.5em; color: #ffffff; margin-bottom: 20px; font-weight: bold; }
        .victory-btn {
            background-color: #00bfff; color: white; border: none; padding: 12px 24px;
            border-radius: 25px; font-size: 1.1em; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block;
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💙 Duel d'Amour & Points Stratégiques</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    {% if winner %}
    <div class="victory-overlay">
        <div class="victory-card">
            <div class="victory-title">🌸 VICTOIRE ÉPIQUE DE L'AMOUR ! 💐</div>
            <div class="victory-flowers">🌸 🌺 🌷 🌹 🌻 💐 🌸</div>
            <div class="victory-name">Le grand vainqueur :<br><span style="color: #00ffff;">{{ winner }}</span></div>
            <div class="victory-flowers">🌸 🌺 🌷 🌹 🌻 💐 🌸</div>
            <p style="color: #e4e6eb; margin-bottom: 20px; font-size: 0.9em;">L'adversaire est à 0 point ! Il a perdu et doit céder !</p>
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
                <span>🎯 POINTS (SEUILS ANIMAUX) :</span>
                {% for user, pts in scores.items() %}
                    <span>{{ user }} : {{ pts }} pts</span>
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
                            <div class="judge-info">🏆 {{ m.comment }}</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa /lion [message][faille] ou /bouclier..." required autocomplete="off">
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
    
    if sender not in game_state["scores"]:
        game_state["scores"][sender] = 50

    if text:
        lower_text = text.lower()
        avatar = "👤"
        extra_class = ""
        comment = "Message de drague classique."
        transfer_points = 20

        # Utilisation du bouclier magique unique
        if lower_text.startswith('/bouclier'):
            if game_state["shield_used"].get(sender, False):
                comment = "🛡️ Erreur : Tu as déjà utilisé ton bouclier unique !"
                formatted_text = "🛡️ *Tentative de bouclier (Déjà épuisé)*"
            else:
                game_state["shield_used"][sender] = True
                comment = f"🛡️ Bouclier activé ! {sender} bloque l'attaque adverse !"
                formatted_text = "🛡️ **BOUCLIER MAGIQUE ACTIVÉ !** Attaque bloquée !"
                game_state["last_animal_power"] = 0
                game_state["last_animal_name"] = None

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "🛡️",
                "text": formatted_text,
                "comment": comment,
                "extra_class": "animal-strategy"
            })
            return redirect(url_for('index'))

        # Détection d'un animal (Bestiaire infini & vérification des seuils de points)
        animal_match = re.match(r'^/([a-zA-Zà-öø-ÿ]+)', lower_text)
        
        if animal_match:
            animal_name_raw = animal_match.group(1)
            animal_name = animal_name_raw.capitalize()
            
            # Définition de la puissance et du coût requis en points pour invoquer l'animal
            apex_predators = ['dragon', 'phénix', 'licorne', 'titan', 'kraken', 'lion', 'tigre', 'ours', 'loup']
            small_animals = ['lapin', 'chat', 'souris', 'grenouille', 'oiseau', 'fourmi']
            
            if animal_name_raw in apex_predators:
                power = 5
                required_points = 50 # Le lion, dragon, etc. exigent au moins 50 points
            elif animal_name_raw in small_animals:
                power = 1
                required_points = 0 # Accessible tout de suite
            else:
                power = 3
                required_points = 25

            # Vérification si le joueur a assez de points pour débloquer/utiliser cet animal
            current_player_points = game_state["scores"].get(sender, 50)
            if current_player_points < required_points:
                game_state["messages"].append({
                    "sender": "Système d'Arbitrage",
                    "role": "Arbitre",
                    "avatar": "⚠️",
                    "text": f"❌ **Invocation Impossible !** Tu n'as que {current_player_points} pts, mais le **{animal_name}** exige un minimum de **{required_points} pts** pour être débloqué et utilisé !",
                    "comment": "Seuil de points insuffisant",
                    "extra_class": "animal-strategy"
                })
                return redirect(url_for('index'))

            avatar = "🐾"
            extra_class = "animal-strategy"

            parts = re.findall(r'\[(.*?)\]', text)
            main_msg = parts[0] if len(parts) > 0 else text[len(animal_match.group(0)):].strip()
            faille_msg = parts[1] if len(parts) > 1 else ""

            prev_power = game_state.get("last_animal_power", 0)
            prev_name = game_state.get("last_animal_name", "aucun")
            has_valid_faille = len(faille_msg.strip()) > 3

            # Résolution du combat, des failles et du transfert de points
            if prev_power > 0 and prev_power != power:
                if power < prev_power:
                    if has_valid_faille:
                        transfer_points = 35
                        comment = f"🧠 Le {animal_name} gagne par la ruse (faille : « {faille_msg} ») ! Il triomphe du {prev_name} et récupère les points !"
                    else:
                        transfer_points = -35 # Le joueur perd des points au profit de l'autre
                        comment = f"🛡️ Le {prev_name} est plus fort que ton {animal_name} et aucune faille n'a été trouvée ! Le {prev_name} l'emporte, tu n'as pas le choix, tu dois céder !"
                elif power > prev_power:
                    transfer_points = 40
                    comment = f"⚔️ Le {animal_name} surclasse le {prev_name} ! Il gagne le duel haut la main, tu n'as pas le choix, tu dois céder !"
                else:
                    transfer_points = 15
                    comment = f"⚖️ Égalité parfaite entre les bêtes."
            else:
                transfer_points = 25
                comment = f"✨ Le {animal_name} frappe fort ! L'adversaire est bousculé."

            game_state["last_animal_power"] = power
            game_state["last_animal_name"] = animal_name

            formatted_text = f"🗣️ « {main_msg} »" + (f" 🔍 [FAILLE : {faille_msg}]" if faille_msg else "")
            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": avatar,
                "text": formatted_text,
                "comment": comment,
                "extra_class": extra_class
            })

        else:
            game_state["last_animal_power"] = 0
            game_state["last_animal_name"] = None
            transfer_points = 20
            comment = "💙 Message de drague validé, transfert de points vers le séducteur !"

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "👤",
                "text": text,
                "comment": comment,
                "extra_class": ""
            })

        # Transfert réel des points entre les joueurs et vérification de la défaite à 0 point
        for p in list(game_state["scores"].keys()):
            if p == sender:
                if animal_match and transfer_points < 0:
                    pass # Ne gagne pas de points si l'attaque animale rate sans faille
                else:
                    game_state["scores"][p] += abs(transfer_points)
            else:
                game_state["scores"][p] -= abs(transfer_points)
                if game_state["scores"][p] <= 0:
                    game_state["scores"][p] = 0
                    game_state["winner"] = sender # Le joueur actuel gagne, l'autre tombe à 0 et a perdu

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
    game_state["last_animal_power"] = 0
    game_state["last_animal_name"] = None
    game_state["shield_used"] = {}
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)