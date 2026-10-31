from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

game_state = {
    "messages": [],
    "scores": {"Séducteur": 50, "Défenseur (Cible)": 50},
    "winner": None
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Duel d'Amour</title>
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
        .msg-bubble.love-trap {
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
        <div class="header-title">💖 Duel d'Amour & Bestiaire</div>
        <a href="/reset" class="reset-btn">Réinitialiser</a>
    </div>

    {% if winner %}
    <div class="victory-overlay">
        <div class="victory-card">
            <div class="victory-title">💘 COUP DE FOUDRE TOTAL ! 💖</div>
            <div class="victory-name">Le grand vainqueur de l'amour :<br><span style="color: #00ffff;">{{ winner }}</span></div>
            <p style="color: #e4e6eb; margin-bottom: 20px; font-size: 0.9em;">L'autre a complètement succombé et a perdu son cœur !</p>
            <a href="/reset" class="victory-btn">Nouvelle Partie 🔄</a>
        </div>
    </div>
    {% endif %}

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="config-row">
                <input type="text" name="username" placeholder="Votre Nom (ex: Tsanta, Tiffanie)" autocomplete="off">
                <!-- Choix des avatars / animaux aux caractères uniques -->
                <select name="role">
                    <option value="Renard">🦊 Renard (Fourbe & Séducteur)</option>
                    <option value="Loup">🐺 Loup (Passionné & Protecteur)</option>
                    <option value="Chat">🐱 Chat (Mystérieux & Indifférent)</option>
                    <option value="Dragon">🐉 Dragon (Feu & Amour Absolu)</option>
                    <option value="Ange">👼 Ange (Pureté & Charme Céleste)</option>
                    <option value="Phoenix">🔥 Phoenix (Renaissance Amoureuse)</option>
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
            <input type="text" name="text" class="message-input" placeholder="Aa Envoie ta drague ou ta résistance..." required autocomplete="off">
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
    role = request.form.get('role', 'Renard')
    text = request.form.get('text', '').strip()
    
    if text:
        # Base de données des animaux et créatures avec leurs caractères naturels et questions pièges automatiques
        animals_traits = {
            "Renard": {
                "emoji": "🦊", 
                "trap": "🦊 *[Piège du Renard rusé]* : « Dis-moi... Si tu devais me voler un secret rien qu'à toi, ce serait lequel ? »", 
                "impact": 15, "desc": "Utilise la ruse pour faire douter et charmer l'autre."
            },
            "Loup": {
                "emoji": "🐺", 
                "trap": "🐺 *[Piège du Loup solitaire]* : « La meute s'en fout, mais moi je ne vois que toi. Pourquoi est-ce que tu m'envoutes autant ? »", 
                "impact": 20, "desc": "Séduction intense et magnétique."
            },
            "Chat": {
                "emoji": "🐱", 
                "trap": "🐱 *[Piège du Chat indifférent]* : « Je pourrais ignorer ton message et m'endormir au soleil... Mais pourquoi est-ce que j'ai envie de ronronner près de toi à la place ? »", 
                "impact": 18, "desc": "Joue l'indifférence pour attirer irrésistiblement."
            },
            "Dragon": {
                "emoji": "🐉", 
                "trap": "🐉 *[Piège du Dragon ardent]* : « Mon cœur brûle plus fort que mes flammes. Es-tu prêt(e) à te consumer d'amour avec moi ? »", 
                "impact": 25, "desc": "Brûle les défenses amoureuses en un instant."
            },
            "Ange": {
                "emoji": "👼", 
                "trap": "👼 *[Piège Céleste]* : « On dit que les anges n'ont pas de cœur... Alors dis-moi pourquoi le mien bat si fort quand tu parles ? »", 
                "impact": 22, "desc": "Charme angélique irrésistible."
            },
            "Phoenix": {
                "emoji": "🔥", 
                "trap": "🔥 *[Piège de la Renaissance]* : « Même si mes sentiments brûlent et se réduisent en cendres, je retombe amoureux de toi à chaque seconde. »", 
                "impact": 25, "desc": "Amour éternel et incandescent."
            }
        }

        trait = animals_traits.get(role, animals_traits["Renard"])
        avatar = trait["emoji"]
        
        # Le message automatique généré par le caractère de l'animal (question piège)
        trap_message = trait["trap"]

        # Analyse du texte de l'utilisateur (si romantique ou résistant)
        lower_text = text.lower()
        if any(w in lower_text for w in ['amour', 't’aime', 'coeur', 'oui', 'tiako', 'ensemble', 'viens']):
            comment = f"💘 Coup de cœur ! Le charme de l'{role} fait monter la température !"
            impact = trait["impact"]
        else:
            comment = f"🛡️ Résistance active ! L'autre essaie de parer la séduction."
            impact = -5 # Défense

        # Mettre à jour les scores (Jauge d'amour de 0 à 100)
        # On attribue le score à l'adversaire ou au joueur
        players = list(game_state["scores"].keys())
        if sender not in players:
            if len(players) < 2:
                game_state["scores"][sender] = 50
            else:
                # Remplacer un joueur par défaut ou assigner
                pass

        # Simulation de la progression amoureuse
        for p in game_state["scores"]:
            if p != sender:
                game_state["scores"][p] += impact
                if game_state["scores"][p] > 100:
                    game_state["scores"][p] = 100
                if game_state["scores"][p] <= 0:
                    game_state["scores"][p] = 0
                    game_state["winner"] = sender # Le séducteur gagne

        # Enregistrement du message de l'utilisateur
        game_state["messages"].append({
            "sender": sender,
            "role": role,
            "avatar": avatar,
            "text": text,
            "comment": comment,
            "extra_class": ""
        })

        # Envoi automatique de la question piège liée au caractère de l'animal
        game_state["messages"].append({
            "sender": f"Piège ({role})",
            "role": role,
            "avatar": avatar,
            "text": trap_message,
            "comment": f"Caractère naturel : {trait['desc']}",
            "extra_class": "love-trap"
        })
        
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
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)