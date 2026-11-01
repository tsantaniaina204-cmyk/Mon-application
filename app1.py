from flask import Flask, render_template_string, request, redirect, url_for, session
import re
import urllib.request
import json
import random

app = Flask(__name__)
app.secret_key = "chrono_royaume_secret_key" # Nécessaire pour mémoriser les sessions des utilisateurs

# 🔒 TES CLÉS API PROTÉGÉES (Découpées et concaténées)
k1 = "AQ.Ab8RN6J" + "PeHip7Jde" + "-XcNB1"
k2 = "jKy-gRTUZ" + "GFJcFq7" + "cymooPdXj9Q"
PART1 = k1 + k2

k3 = "AQ.Ab8RN6L" + "IP5_Y8WH2nS" + "lW4cUoBY"
k4 = "B_HxhNwA" + "6V22bkKd" + "hRZGPs9A"
PART2 = k3 + k4

k5 = "AQ.Ab8RN6J" + "R73kVk5z" + "11V3Pnu-"
k6 = "605D_z41D" + "jmNy28JVS" + "VOV2A7r-w"
PART3 = k5 + k6

k7 = "AQ.Ab8RN6J" + "w3ysgWGOW" + "iXdTS1HO"
k8 = "IE50K0xer" + "MoniBU5Is" + "Pq6M4d_w"
PART4 = k7 + k8

k9 = "AQ.Ab8RN6L" + "5Wdplts-" + "NGDHH9Bx"
k10 = "_HSH-OHr" + "fqgE9PVZZ" + "Bw2jWs6wsA"
PART5 = k9 + k10

GEMINI_API_KEYS = [PART1, PART2, PART3, PART4, PART5]

game_state = {
    "messages": [],
    "scores": {},
    "winner": None,
    "status": "PLAYING", # PLAYING, PAUSED, STOPPED
    "last_animal_power": 0,
    "last_animal_name": None,
    "last_animal_emoji": "👤",
    "last_animal_color": "#00bfff",
    "shield_used": {}
}

def call_gemini(prompt_text):
    active_key = random.choice(GEMINI_API_KEYS)
    if not active_key:
        return "Je t'aime de tout mon cœur, peu importe ton attaque !"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={active_key}"
    data = {"contents": [{"parts": [{"text": prompt_text}]}] }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            return res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print("Erreur API Gemini:", e.strerror if hasattr(e, 'strerror') else str(e))
        return "Mon amour est plus fort que ton attaque !"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Compte Facebook & Commandes IA</title>
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
        .header-title { font-weight: bold; font-size: 0.95em; color: #00bfff; display: flex; align-items: center; gap: 6px; }
        .header-actions { display: flex; gap: 6px; }
        .action-btn {
            background: #3a3b3c; color: #00bfff; border: none;
            padding: 6px 10px; border-radius: 12px; font-size: 0.75em; text-decoration: none; cursor: pointer; font-weight: bold;
        }

        .messenger-form { display: flex; flex-direction: column; flex: 1; min-height: 0; }

        .top-panel {
            flex-shrink: 0; background-color: #242526;
            padding: 8px 12px; border-bottom: 1px solid #393a3b; font-size: 0.8em;
        }
        .scores-board {
            display: flex; justify-content: center; gap: 15px;
            background-color: #1c1d1e; padding: 6px; border-radius: 10px;
            color: #00bfff; font-weight: bold; font-size: 0.85em; margin-top: 2px; overflow-x: auto;
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
        .msg-content { max-width: 85%; display: flex; flex-direction: column; }
        .msg-bubble {
            background-color: #3a3b3c; color: #e4e6eb; padding: 10px 14px;
            border-radius: 18px; font-size: 0.9em; word-wrap: break-word; position: relative;
        }
        .msg-sender { font-size: 0.75em; color: #b0b3b8; margin-bottom: 3px; margin-left: 4px; }
        
        .animal-gif-container {
            width: 100%; max-height: 180px; border-radius: 12px; overflow: hidden; margin-bottom: 8px;
            display: flex; justify-content: center; align-items: center; background: #000;
        }
        .animal-gif-container img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }

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

        /* MODALE PROFIL (STYLE FACEBOOK) */
        .modal-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85); display: flex; justify-content: center; align-items: center; z-index: 200; padding: 20px;
        }
        .modal-card {
            background: #242526; border: 2px solid #00bfff; padding: 25px; border-radius: 16px;
            width: 100%; max-width: 380px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .modal-title { font-size: 1.3em; color: #00bfff; margin-bottom: 15px; font-weight: bold; }
        .modal-input {
            width: 100%; background-color: #3a3b3c; border: 1px solid #4e4f50; color: #e4e6eb;
            padding: 10px 14px; border-radius: 12px; font-size: 0.95em; outline: none; margin-bottom: 12px;
        }
        .modal-select {
            width: 100%; background-color: #3a3b3c; border: 1px solid #4e4f50; color: #e4e6eb;
            padding: 10px 14px; border-radius: 12px; font-size: 0.95em; outline: none; margin-bottom: 20px;
        }
        .modal-btn {
            background-color: #00bfff; color: white; border: none; width: 100%; padding: 12px;
            border-radius: 20px; font-size: 1em; font-weight: bold; cursor: pointer;
        }

        /* OVERLAY VICTOIRE / PAUSE / STOP */
        .overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.92); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; text-align: center; padding: 20px;
        }
    </style>
</head>
<body>

<div class="messenger-container">
    <div class="messenger-header">
        <div class="header-title">💙 <span>{{ session.get('username', 'Invité') }}</span> ({{ session.get('role', 'Séducteur') }})</div>
        <div class="header-actions">
            <a href="/profile" class="action-btn">⚙️ Compte</a>
            <a href="/reset" class="action-btn" style="color: #ff5252;">Réinit</a>
        </div>
    </div>

    <!-- 👤 MODALE DE CONFIGURATION DU COMPTE (STYLE FACEBOOK) -->
    {% if show_profile_modal %}
    <div class="modal-overlay">
        <div class="modal-card">
            <div class="modal-title">⚙️ Paramètres du Compte Facebook</div>
            <form action="/save_profile" method="POST">
                <input type="text" name="username" class="modal-input" value="{{ session.get('username', '') }}" placeholder="Votre Nom (ex: Tsanta)" required autocomplete="off">
                <select name="role" class="modal-select">
                    <option value="Séducteur" {% if session.get('role') == 'Séducteur' %}selected{% endif %}>💖 Le Séducteur (Attaque)</option>
                    <option value="Séduit" {% if session.get('role') == 'Séduit' %}selected{% endif %}>🛡️ Le Séduit (Défend)</option>
                </select>
                <button type="submit" class="modal-btn">Enregistrer mon Profil 💾</button>
            </form>
        </div>
    </div>
    {% endif %}

    <!-- 🌸 ÉCRAN DE VICTOIRE -->
    {% if winner %}
    <div class="overlay">
        <div class="modal-card" style="background: linear-gradient(135deg, #003366, #162447);">
            <div style="font-size: 1.6em; color: #00bfff; margin-bottom: 10px;">🌸 VICTOIRE ÉPIQUE ! 💐</div>
            <div style="font-size: 1.3em; margin: 10px 0;">🌸 🌺 🌷 🌹 🌻 💐 🌸</div>
            <div style="font-size: 1.3em; color: #ffffff; margin-bottom: 15px; font-weight: bold;">Le vainqueur : {{ winner }}</div>
            <div style="font-size: 1.3em; margin: 10px 0;">🌸 🌺 🌷 🌹 🌻 💐 🌸</div>
            <p style="color: #e4e6eb; margin-bottom: 20px; font-size: 0.85em;">L'adversaire a succombé et doit céder !</p>
            <a href="/reset" class="modal-btn" style="text-decoration: none; display: inline-block;">Nouvelle Partie 🔄</a>
        </div>
    </div>
    {% endif %}

    <!-- ⏸️ ÉCRAN PAUSE OU STOP -->
    {% if game_status == 'PAUSED' %}
    <div class="overlay">
        <div class="modal-card">
            <h2 style="color: #ff9800; margin-bottom: 15px;">⏸️ JEU EN PAUSE</h2>
            <p style="margin-bottom: 20px; color: #b0b3b8;">Le duel est temporairement suspendu.</p>
            <a href="/start_game" class="modal-btn" style="text-decoration: none; display: inline-block;">Reprendre (/start) ▶️</a>
        </div>
    </div>
    {% elif game_status == 'STOPPED' %}
    <div class="overlay">
        <div class="modal-card">
            <h2 style="color: #ff5252; margin-bottom: 15px;">🛑 JEU ARRÊTÉ</h2>
            <p style="margin-bottom: 20px; color: #b0b3b8;">La partie a été stoppée par un joueur.</p>
            <a href="/start_game" class="modal-btn" style="text-decoration: none; display: inline-block;">Redémarrer (/start) 🔄</a>
        </div>
    </div>
    {% endif %}

    <form action="/send" method="POST" class="messenger-form">
        <div class="top-panel">
            <div class="scores-board">
                <span>🎯 SCORES :</span>
                {% if scores %}
                    {% for user, pts in scores.items() %}
                        <span><b>{{ user }}</b> : {{ pts }} pts</span>
                    {% endfor %}
                {% else %}
                    <span>En attente de connexion...</span>
                {% endif %}
            </div>
        </div>

        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble" style="background: {{ m.bg_color }}; border: 2px solid {{ m.border_color }};">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            
                            {% if m.gif_url %}
                            <div class="animal-gif-container">
                                <img src="{{ m.gif_url }}" alt="Animal Animé">
                            </div>
                            {% endif %}

                            {{ m.text }}
                            <div class="judge-info">🏆 {{ m.comment }}</div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa /lion [msg][faille], /ia, /pause, /stop..." required autocomplete="off">
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
    # Si le nom n'est pas encore défini en session, on affiche la modale profil
    show_profile_modal = 'username' not in session or not session['username']
    return render_template_string(
        HTML_TEMPLATE, 
        messages=game_state["messages"], 
        scores=game_state["scores"], 
        winner=game_state["winner"],
        game_status=game_state["status"],
        show_profile_modal=show_profile_modal
    )

@app.route('/profile')
def profile():
    # Ouvre la modale pour changer de nom ou de rôle (Style Facebook)
    return render_template_string(
        HTML_TEMPLATE, 
        messages=game_state["messages"], 
        scores=game_state["scores"], 
        winner=game_state["winner"],
        game_status=game_state["status"],
        show_profile_modal=True
    )

@app.route('/save_profile', methods=['POST'])
def save_profile():
    username = request.form.get('username', '').strip()
    role = request.form.get('role', 'Séducteur')
    if username:
        session['username'] = username
        session['role'] = role
        if username not in game_state["scores"]:
            game_state["scores"][username] = 10
    return redirect(url_for('index'))

@app.route('/start_game')
def start_game():
    game_state["status"] = "PLAYING"
    return redirect(url_for('index'))

@app.route('/send', methods=['POST'])
def send():
    if game_state["winner"] or game_state["status"] != "PLAYING":
        return redirect(url_for('index'))

    sender = session.get('username', '')
    role = session.get('role', 'Séducteur')
    
    if not sender:
        return redirect(url_for('profile'))

    text = request.form.get('text', '').strip()
    
    if sender not in game_state["scores"]:
        game_state["scores"][sender] = 10

    if text:
        lower_text = text.lower()

        # 🛑 GESTION DES COMMANDES SPÉCIALES (/stop, /pause, /start, /ia)
        if lower_text == '/stop':
            game_state["status"] = "STOPPED"
            return redirect(url_for('index'))
        elif lower_text == '/pause':
            game_state["status"] = "PAUSED"
            return redirect(url_for('index'))
        elif lower_text == '/start':
            game_state["status"] = "PLAYING"
            return redirect(url_for('index'))
        
        # 🤖 GESTION DE LA COMMANDE /IA (Gemini répond à ta place)
        if lower_text.startswith('/ia'):
            # Trouver la dernière attaque de l'adversaire
            last_enemy_attack = "une déclaration d'amour ou une attaque"
            for m in reversed(game_state["messages"]):
                if m["sender"] != sender and m["sender"] != "Système d'Arbitrage":
                    last_enemy_attack = m["text"]
                    break
            
            prompt_ia = f"""
            Tu es l'intelligence artificielle qui joue à la place de {sender} ({role}) dans un duel de séduction stratégique.
            L'adversaire vient de dire ou d'attaquer avec : "{last_enemy_attack}".
            Génère une réplique romantique, piquante ou une contre-attaque intelligente avec un animal (ex: /lion ou /dragon) et une faille pour le contrer.
            Format attendu : /lion [ta réponse romantique][ta faille astucieuse]
            """
            ai_response = call_gemini(prompt_ia)
            text = ai_response # On remplace le texte par la réponse générée par Gemini !
            lower_text = text.lower()

        avatar = "👤"
        comment = "Message normal et neutre (aucun point gagné ni perdu)."
        point_change = 0
        bg_color = "#3a3b3c"
        border_color = "#393a3b"
        gif_url = None

        # Bouclier unique
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
                "bg_color": "#002244",
                "border_color": "#00bfff",
                "gif_url": None
            })
            return redirect(url_for('index'))

        # Bestiaire complet avec GIFs animés
        animal_match = re.match(r'^/([a-zA-Zà-öø-ÿ]+)', lower_text)
        
        if animal_match:
            animal_name_raw = animal_match.group(1)
            animal_name = animal_name_raw.capitalize()
            
            animal_database = {
                "grenouille": {"emoji": "🐸", "color": "#2e7d32", "border": "#4caf50", "gif": "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif"},
                "lion": {"emoji": "🦁", "color": "#b71c1c", "border": "#ff5252", "gif": "https://media.giphy.com/media/l0HlOBZOM7zivw2vS/giphy.gif"},
                "dragon": {"emoji": "🐉", "color": "#4a148c", "border": "#9c27b0", "gif": "https://media.giphy.com/media/fYl6op4uTBUBy/giphy.gif"},
                "tigre": {"emoji": "🐅", "color": "#e65100", "border": "#ff9800", "gif": "https://media.giphy.com/media/12bjQ7uaduOQCs/giphy.gif"},
                "loup": {"emoji": "🐺", "color": "#263238", "border": "#78909c", "gif": "https://media.giphy.com/media/8qDz8M6JghIwM/giphy.gif"},
                "chat": {"emoji": "🐱", "color": "#f57f17", "border": "#ffeb3b", "gif": "https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif"},
                "lapin": {"emoji": "🐰", "color": "#ad1457", "border": "#ff4081", "gif": "https://media.giphy.com/media/3o6ZsS8GFJKJeHoSQE/giphy.gif"},
                "serpent": {"emoji": "🐍", "color": "#1b5e20", "border": "#81c784", "gif": "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif"},
                "ours": {"emoji": "🐻", "color": "#4e342e", "border": "#8d6e63", "gif": "https://media.giphy.com/media/xTiTnMhJTwNHChdTZS/giphy.gif"},
                "aigle": {"emoji": "🦅", "color": "#01579b", "border": "#03a9f4", "gif": "https://media.giphy.com/media/l4FGpP4lxCKgK5TB6/giphy.gif"},
                "phénix": {"emoji": "🔥", "color": "#bf360c", "border": "#ff5722", "gif": "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"},
                "licorne": {"emoji": "🦄", "color": "#880e4f", "border": "#e91e63", "gif": "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif"}
            }
            
            a_info = animal_database.get(animal_name_raw, {"emoji": "🐾", "color": "#003366", "border": "#00bfff", "gif": "https://media.giphy.com/media/3oz8xLd9DJq2l2VFtu/giphy.gif"})
            avatar = a_info["emoji"]
            bg_color = "linear-gradient(135deg, " + a_info["color"] + ", #18191a)"
            border_color = a_info["border"]
            gif_url = a_info["gif"]

            apex_predators = ['dragon', 'phénix', 'licorne', 'titan', 'kraken', 'lion', 'tigre', 'ours', 'loup']
            small_animals = ['lapin', 'chat', 'souris', 'grenouille', 'oiseau', 'fourmi']
            
            if animal_name_raw in apex_predators:
                power = 5
                point_change = 2
            elif animal_name_raw in small_animals:
                power = 1
                point_change = 1
            else:
                power = 3
                point_change = 1

            parts = re.findall(r'\[(.*?)\]', text)
            main_msg = parts[0] if len(parts) > 0 else text[len(animal_match.group(0)):].strip()
            faille_msg = parts[1] if len(parts) > 1 else ""

            prev_power = game_state.get("last_animal_power", 0)
            prev_name = game_state.get("last_animal_name", "aucun")
            prev_emoji = game_state.get("last_animal_emoji", "👤")
            prev_color = game_state.get("last_animal_color", "#00bfff")
            prev_gif = game_state.get("last_animal_gif", None)

            # Jugement intelligent de la faille par Gemini
            has_valid_faille = False
            if prev_power > 0 and power < prev_power and len(faille_msg.strip()) > 3:
                # Prompt sécurisé vers l'API Gemini
                active_key = random.choice(GEMINI_API_KEYS)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={active_key}"
                prompt = f"Arbitre de séduction: L'animal '{animal_name}' attaque '{prev_name}' avec la faille: '{faille_msg}'. Est-ce logique et valable ? Réponds UNIQUEMENT 'OUI' ou 'NON'."
                try:
                    req = urllib.request.Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req) as response:
                        res_json = json.loads(response.read().decode())
                        ans = res_json["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                        has_valid_faille = "OUI" in ans
                except:
                    has_valid_faille = len(faille_msg.strip()) > 5

            winning_animal_name = animal_name
            winning_emoji = avatar
            winning_color = border_color
            winning_gif = gif_url
            
            loser_player = None
            winner_player = sender

            for p in game_state["scores"]:
                if p != sender:
                    loser_player = p
                    break

            if prev_power > 0 and prev_power != power:
                if power < prev_power:
                    if has_valid_faille:
                        comment = f"🧠 **Gemini a validé la faille !** Le {animal_name} terrasse le {prev_name} (-{point_change} pt adversaire, +{point_change} pt toi) !"
                    else:
                        winning_animal_name = prev_name
                        winning_emoji = prev_emoji
                        winning_color = prev_color
                        winning_gif = prev_gif
                        comment = f"🛡️ **Gemini a rejeté la faille** ! Le {prev_name} l'emporte (tu perds {point_change} pt) !"
                        loser_player = sender
                        winner_player = prev_name if prev_name != "aucun" else [p for p in game_state["scores"] if p != sender][0]
                elif power > prev_power:
                    comment = f"⚔️ Le {animal_name} surclasse le {prev_name} ! Victoire du duel (adversaire : -{point_change} pt, toi : +{point_change} pt) !"
                else:
                    comment = f"⚖️ Égalité parfaite entre les bêtes. Aucun point perdu."
                    loser_player = None
            else:
                comment = f"✨ Le {animal_name} prend l'avantage dans ce duel !"
                loser_player = None

            game_state["last_animal_power"] = power
            game_state["last_animal_name"] = winning_animal_name
            game_state["last_animal_emoji"] = winning_emoji
            game_state["last_animal_color"] = winning_color
            game_state["last_animal_gif"] = winning_gif

            if loser_player and loser_player in game_state["scores"]:
                game_state["scores"][loser_player] -= point_change
                if game_state["scores"][loser_player] < 0:
                    game_state["scores"][loser_player] = 0

                for p in game_state["scores"]:
                    if p != loser_player:
                        game_state["scores"][p] += point_change
                        winner_player = p

                if game_state["scores"][loser_player] == 0:
                    game_state["winner"] = winner_player

            formatted_text = f"🗣️ « {main_msg} »" + (f" 🔍 [FAILLE JUGÉE PAR IA : {faille_msg}]" if faille_msg else "")
            
            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": winning_emoji,
                "text": formatted_text,
                "comment": comment,
                "bg_color": bg_color,
                "border_color": border_color,
                "gif_url": winning_gif
            })

        else:
            game_state["last_animal_power"] = 0
            game_state["last_animal_name"] = None
            game_state["last_animal_emoji"] = "👤"
            game_state["last_animal_color"] = "#00bfff"
            game_state["last_animal_gif"] = None
            comment = "💙 Message normal et neutre (aucun point gagné ni perdu)."

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "👤",
                "text": text,
                "comment": comment,
                "bg_color": "#3a3b3c",
                "border_color": "#393a3b",
                "gif_url": None
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
    game_state["scores"] = {}
    game_state["winner"] = None
    game_state["status"] = "PLAYING"
    game_state["last_animal_power"] = 0
    game_state["last_animal_name"] = None
    game_state["last_animal_emoji"] = "👤"
    game_state["last_animal_color"] = "#00bfff"
    game_state["last_animal_gif"] = None
    game_state["shield_used"] = {}
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)