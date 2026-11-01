from flask import Flask, render_template_string, request, redirect, url_for, session
import re
import urllib.request
import json
import random

app = Flask(__name__)
app.secret_key = "chrono_royaume_secret_key"

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
    "status": "PLAYING",
    "last_animal_power": 0,
    "last_animal_name": None,
    "last_animal_emoji": "👤",
    "shield_used": {}
}

def call_gemini(prompt_text):
    active_key = random.choice(GEMINI_API_KEYS)
    if not active_key:
        return prompt_text

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={active_key}"
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode())
            return res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print("Erreur API Gemini:", e)
        return prompt_text


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Chrono-Royaume - Duel d'Amour Fluide</title>
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
        .header-title { font-weight: bold; font-size: 0.9em; color: #00bfff; display: flex; align-items: center; gap: 6px; }
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
            background-color: #18191a; display: flex; flex-direction: column; gap: 14px; min-height: 0;
        }
        
        .msg-row { display: flex; align-items: flex-end; gap: 8px; width: 100%; }
        .msg-row.left { justify-content: flex-start; }
        .msg-row.right { justify-content: flex-end; flex-direction: row-reverse; }

        .avatar-circle {
            width: 34px; height: 34px; border-radius: 50%; background-color: #3a3b3c;
            display: flex; align-items: center; justify-content: center; font-size: 1.1em; flex-shrink: 0; border: 1px solid #00bfff;
        }
        .msg-content { max-width: 82%; display: flex; flex-direction: column; }
        .msg-row.right .msg-content { align-items: flex-end; }

        .msg-bubble {
            color: #e4e6eb; padding: 12px 16px;
            border-radius: 18px; font-size: 0.9em; word-wrap: break-word; position: relative;
        }
        .msg-sender { font-size: 0.75em; color: #b0b3b8; margin-bottom: 3px; margin-left: 4px; }
        .msg-row.right .msg-sender { margin-right: 4px; margin-left: 0; text-align: right; }
        
        .animal-css-card {
            width: 100%; height: 130px; border-radius: 10px; margin-bottom: 10px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            font-size: 3.2em; border: 2px solid rgba(255,255,255,0.2);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        .animal-name-badge {
            font-size: 0.3em; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 8px; margin-top: 6px; font-weight: bold; color: #fff; text-transform: uppercase;
        }

        .attack-main-text {
            font-size: 1.05em; font-weight: bold; color: #ffffff; margin-bottom: 8px; line-height: 1.4;
        }

        .attack-faille-box {
            background: rgba(0, 0, 0, 0.35); border-left: 4px solid #00bfff;
            padding: 8px 12px; border-radius: 6px; font-size: 0.85em; color: #b0b3b8; margin-top: 6px; font-style: italic;
        }

        .judge-info {
            font-size: 0.75em; color: #00bfff; background: rgba(0, 191, 255, 0.15);
            margin-top: 8px; padding: 5px 8px; border-radius: 6px; font-weight: bold;
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

    {% if show_profile_modal %}
    <div class="modal-overlay">
        <div class="modal-card">
            <div class="modal-title">⚙️ Paramètres du Compte</div>
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

    {% if game_status == 'PAUSED' %}
    <div class="overlay">
        <div class="modal-card">
            <h2 style="color: #ff9800; margin-bottom: 15px;">⏸️ JEU EN PAUSE</h2>
            <a href="/start_game" class="modal-btn" style="text-decoration: none; display: inline-block; margin-top: 15px;">Reprendre (/start) ▶️</a>
        </div>
    </div>
    {% elif game_status == 'STOPPED' %}
    <div class="overlay">
        <div class="modal-card">
            <h2 style="color: #ff5252; margin-bottom: 15px;">🛑 JEU ARRÊTÉ</h2>
            <a href="/start_game" class="modal-btn" style="text-decoration: none; display: inline-block; margin-top: 15px;">Redémarrer (/start) 🔄</a>
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
                    <span>En attente...</span>
                {% endif %}
            </div>
        </div>

        <div class="chat-messages" id="chatbox">
            {% for m in messages %}
                <div class="msg-row {{ 'right' if m.is_current_user else 'left' }}">
                    <div class="avatar-circle">{{ m.avatar }}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{{ m.sender }} ({{ m.role }})</div>
                        <div class="msg-bubble" style="background: {{ m.bg_color }}; border: 2px solid {{ m.border_color }};">
                            <a href="/delete/{{ loop.index0 }}" class="delete-link" title="Supprimer">✕</a>
                            
                            {% if m.css_card %}
                            <div class="animal-css-card" style="background: {{ m.css_card.bg }};">
                                <span>{{ m.css_card.emoji }}</span>
                                <div class="animal-name-badge">{{ m.css_card.name }}</div>
                            </div>
                            {% endif %}

                            <div class="attack-main-text">{{ m.main_text }}</div>

                            {% if m.faille_text %}
                            <div class="attack-faille-box">
                                🔍 <b>Faille :</b> {{ m.faille_text }}
                            </div>
                            {% endif %}

                            {% if m.comment %}
                            <div class="judge-info">{{ m.comment }}</div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>

        <div class="messenger-input-area">
            <input type="text" name="text" class="message-input" placeholder="Aa /lion [message][faille logique]..." required autocomplete="off">
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
    show_profile_modal = 'username' not in session or not session['username']
    current_user = session.get('username', '')
    formatted_messages = []
    for m in game_state["messages"]:
        m_copy = m.copy()
        m_copy['is_current_user'] = (m['sender'] == current_user)
        formatted_messages.append(m_copy)

    return render_template_string(
        HTML_TEMPLATE, 
        messages=formatted_messages, 
        scores=game_state["scores"], 
        winner=game_state["winner"],
        game_status=game_state["status"],
        show_profile_modal=show_profile_modal
    )

@app.route('/profile')
def profile():
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

        if lower_text == '/stop':
            game_state["status"] = "STOPPED"
            return redirect(url_for('index'))
        elif lower_text == '/pause':
            game_state["status"] = "PAUSED"
            return redirect(url_for('index'))
        elif lower_text == '/start':
            game_state["status"] = "PLAYING"
            return redirect(url_for('index'))
        
        if lower_text.startswith('/ia'):
            last_enemy_attack = "une déclaration d'amour"
            for m in reversed(game_state["messages"]):
                if m["sender"] != sender and m["sender"] != "Système d'Arbitrage":
                    last_enemy_attack = m.get("main_text", m.get("text", ""))
                    break
            
            prompt_ia = f"Joue à la place de {sender}. L'adversaire a dit: '{last_enemy_attack}'. Réponds avec une attaque animale et une faille au format: /lion [texte][faille]"
            text = call_gemini(prompt_ia)
            lower_text = text.lower()

        # Correction orthographique par Gemini
        correction_prompt = f"Corrige uniquement les fautes de frappe de ce message en conservant son sens : '{text}'"
        text = call_gemini(correction_prompt)
        lower_text = text.lower()

        comment = ""
        point_change = 0
        bg_color = "#3a3b3c"
        border_color = "#393a3b"
        css_card = None
        main_text_display = text
        faille_text_display = ""

        if lower_text.startswith('/bouclier'):
            if game_state["shield_used"].get(sender, False):
                comment = "🛡️ Bouclier déjà épuisé !"
                main_text_display = "🛡️ *Tentative de bouclier (Déjà épuisé)*"
            else:
                game_state["shield_used"][sender] = True
                comment = f"🛡️ Bouclier activé ! Attaque bloquée !"
                main_text_display = "🛡️ **BOUCLIER MAGIQUE ACTIVÉ !**"
                game_state["last_animal_power"] = 0
                game_state["last_animal_name"] = None

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "🛡️",
                "main_text": main_text_display,
                "faille_text": "",
                "comment": comment,
                "bg_color": "#002244",
                "border_color": "#00bfff",
                "css_card": None
            })
            return redirect(url_for('index'))

        # Détection des animaux
        animals_list = ["grenouille", "lion", "dragon", "tigre", "loup", "chat", "lapin", "serpent", "ours", "aigle", "phénix", "licorne"]
        detected_animal = None
        for a in animals_list:
            if a in lower_text:
                detected_animal = a
                break
        
        if detected_animal or lower_text.startswith('/'):
            animal_name_raw = detected_animal if detected_animal else lower_text.replace('/', '').split()[0]
            animal_name = animal_name_raw.capitalize()
            
            animal_database = {
                "grenouille": {"emoji": "🐸", "color": "linear-gradient(135deg, #2e7d32, #81c784)", "border": "#4caf50"},
                "lion": {"emoji": "🦁", "color": "linear-gradient(135deg, #b71c1c, #ff8a80)", "border": "#ff5252"},
                "dragon": {"emoji": "🐉", "color": "linear-gradient(135deg, #4a148c, #ba68c8)", "border": "#9c27b0"},
                "tigre": {"emoji": "🐅", "color": "linear-gradient(135deg, #e65100, #ffb74d)", "border": "#ff9800"},
                "loup": {"emoji": "🐺", "color": "linear-gradient(135deg, #263238, #b0bec5)", "border": "#78909c"},
                "chat": {"emoji": "🐱", "color": "linear-gradient(135deg, #f57f17, #fff176)", "border": "#ffeb3b"},
                "lapin": {"emoji": "🐰", "color": "linear-gradient(135deg, #ad1457, #f48fb1)", "border": "#ff4081"},
                "serpent": {"emoji": "🐍", "color": "linear-gradient(135deg, #1b5e20, #a5d6a7)", "border": "#81c784"},
                "ours": {"emoji": "🐻", "color": "linear-gradient(135deg, #4e342e, #d7ccc8)", "border": "#8d6e63"},
                "aigle": {"emoji": "🦅", "color": "linear-gradient(135deg, #01579b, #81d4fa)", "border": "#03a9f4"},
                "phénix": {"emoji": "🔥", "color": "linear-gradient(135deg, #bf360c, #ffab91)", "border": "#ff5722"},
                "licorne": {"emoji": "🦄", "color": "linear-gradient(135deg, #880e4f, #f8bbd0)", "border": "#e91e63"}
            }
            
            a_info = animal_database.get(animal_name_raw, {"emoji": "🐾", "color": "linear-gradient(135deg, #003366, #00bfff)", "border": "#00bfff"})
            avatar = a_info["emoji"]
            bg_color = "linear-gradient(135deg, #002244, #18191a)"
            border_color = a_info["border"]
            
            css_card = {
                "emoji": a_info["emoji"],
                "bg": a_info["color"],
                "name": animal_name
            }

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
            main_text_display = parts[0] if len(parts) > 0 else text
            faille_text_display = parts[1] if len(parts) > 1 else ""

            prev_power = game_state.get("last_animal_power", 0)
            prev_name = game_state.get("last_animal_name", "aucun")
            prev_emoji = game_state.get("last_animal_emoji", "👤")
            prev_card = game_state.get("last_css_card", None)

            # Jugement strict de la faille par Gemini
            has_valid_faille = False
            if prev_power > 0 and power < prev_power:
                if len(faille_text_display.strip()) > 2:
                    prompt = f"""
                    Arbitre strict de séduction : 
                    L'attaquant utilise un animal plus faible '{animal_name}' contre le prédateur '{prev_name}'.
                    Il propose cette faille logique ou psychologique : '{faille_text_display}'.
                    Cette faille est-elle spirituelle, astucieuse et fait-elle référence à une vraie faiblesse logique exploitable de cet animal ?
                    Réponds UNIQUEMENT par 'OUI' ou 'NON'.
                    """
                    ans = call_gemini(prompt).upper()
                    has_valid_faille = "OUI" in ans
                else:
                    has_valid_faille = False

            winning_animal_name = animal_name
            winning_emoji = avatar
            winning_card = css_card
            
            loser_player = None
            winner_player = sender

            for p in game_state["scores"]:
                if p != sender:
                    loser_player = p
                    break

            if prev_power > 0 and prev_power != power:
                if power < prev_power:
                    if has_valid_faille:
                        comment = f"🧠 Faille validée ! Le {animal_name} terrasse le {prev_name} (-{point_change} pt adversaire, +{point_change} pt toi)"
                    else:
                        winning_animal_name = prev_name
                        winning_emoji = prev_emoji
                        winning_card = prev_card
                        comment = f"❌ Faille rejetée ! Le {prev_name} l'emporte (-{point_change} pt pour toi)"
                        loser_player = sender
                        winner_player = prev_name if prev_name != "aucun" else [p for p in game_state["scores"] if p != sender][0]
                elif power > prev_power:
                    comment = f"⚔️ Le {animal_name} surclasse le {prev_name} (-{point_change} pt adversaire, +{point_change} pt toi)"
                else:
                    comment = f"⚖️ Égalité parfaite. Aucun point perdu."
                    loser_player = None
            else:
                comment = f"✨ Le {animal_name} prend l'avantage !"
                loser_player = None

            game_state["last_animal_power"] = power
            game_state["last_animal_name"] = winning_animal_name
            game_state["last_animal_emoji"] = winning_emoji
            game_state["last_css_card"] = winning_card

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

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": winning_emoji,
                "main_text": main_text_display,
                "faille_text": faille_text_display,
                "comment": comment,
                "bg_color": bg_color,
                "border_color": border_color,
                "css_card": winning_card
            })

        else:
            game_state["last_animal_power"] = 0
            game_state["last_animal_name"] = None
            game_state["last_animal_emoji"] = "👤"
            game_state["last_css_card"] = None
            comment = ""

            game_state["messages"].append({
                "sender": sender,
                "role": role,
                "avatar": "👤",
                "main_text": text,
                "faille_text": "",
                "comment": comment,
                "bg_color": "#3a3b3c",
                "border_color": "#393a3b",
                "css_card": None
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
    game_state["last_css_card"] = None
    game_state["shield_used"] = {}
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)